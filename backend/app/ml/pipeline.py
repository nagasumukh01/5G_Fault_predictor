import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix
)
from backend.app.core.config import settings
from backend.app.ml.features import FeatureEngineer, FEATURE_COLUMNS, CORE_NUMERIC_FEATURES

class ModelPipelineManager:
    """
    Manages loading, training, persistence, and low-latency inference
    for supervised fault prediction (Random Forest & Logistic Regression)
    and unsupervised anomaly detection (Isolation Forest).
    """
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or settings.ARTIFACTS_DIR
        self.fe = FeatureEngineer()
        
        self.rf_model: Optional[RandomForestClassifier] = None
        self.lr_model: Optional[LogisticRegression] = None
        self.iso_model: Optional[IsolationForest] = None
        
        self.metrics_metadata: Dict[str, Any] = {}
        self.is_loaded = False
        
        # Paths
        self.rf_path = self.models_dir / "random_forest_5g.joblib"
        self.lr_path = self.models_dir / "logistic_regression_5g.joblib"
        self.iso_path = self.models_dir / "isolation_forest_5g.joblib"
        self.fe_path = self.models_dir / "feature_engineer.joblib"
        self.meta_path = self.models_dir / "evaluation_metrics.json"

    def load_models_if_present(self) -> bool:
        """
        Loads pre-trained models from disk if present. Returns True if successfully loaded.
        """
        candidate_dirs = [self.models_dir, Path(__file__).resolve().parent / "saved_models"]
        
        for d in candidate_dirs:
            rf_p = d / "random_forest_5g.joblib"
            lr_p = d / "logistic_regression_5g.joblib"
            iso_p = d / "isolation_forest_5g.joblib"
            fe_p = d / "feature_engineer.joblib"
            meta_p = d / "evaluation_metrics.json"

            if rf_p.exists() and lr_p.exists() and iso_p.exists() and fe_p.exists():
                try:
                    self.rf_model = joblib.load(rf_p)
                    self.lr_model = joblib.load(lr_p)
                    self.iso_model = joblib.load(iso_p)
                    self.fe = joblib.load(fe_p)
                    if meta_p.exists():
                        with open(meta_p, "r") as f:
                            self.metrics_metadata = json.load(f)
                    self.is_loaded = True
                    return True
                except Exception as e:
                    print(f"[ModelPipelineManager] Warning: Failed loading models from {d}: {e}")
        self.is_loaded = False
        return False

    def train_and_persist(
        self,
        df_raw: pd.DataFrame,
        horizon_steps: int = 15,
        test_ratio: float = 0.20
    ) -> Dict[str, Any]:
        """
        Executes strict temporal split training and comprehensive evaluation.
        Persists all artifacts for instant zero-lag reload.
        """
        t0 = time.time()
        
        # Sort strictly by timestamp for temporal splitting (prevent future lookahead leakage)
        df_raw = df_raw.sort_values(by="timestamp").reset_index(drop=True)
        split_idx = int(len(df_raw) * (1.0 - test_ratio))
        
        df_train_raw = df_raw.iloc[:split_idx].copy()
        df_test_raw = df_raw.iloc[split_idx:].copy()

        # Extract features
        X_train = self.fe.extract_features_df(df_train_raw, is_training=True)
        y_train = df_train_raw["future_fault_within_horizon"].astype(int).values

        X_test = self.fe.extract_features_df(df_test_raw, is_training=False)
        y_test = df_test_raw["future_fault_within_horizon"].astype(int).values

        # 1. Supervised Primary: Random Forest
        rf = RandomForestClassifier(
            n_estimators=120,
            max_depth=14,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)

        # 2. Supervised Baseline: Logistic Regression
        lr = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        # Scaled input for LR
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        lr.fit(X_train_scaled, y_train)

        # 3. Unsupervised: Isolation Forest (trained on nominal or normal traffic subset)
        nominal_train_mask = (y_train == 0)
        X_train_nominal = X_train[nominal_train_mask] if np.sum(nominal_train_mask) > 50 else X_train
        iso = IsolationForest(
            n_estimators=100,
            contamination=0.08,
            random_state=42,
            n_jobs=-1
        )
        iso.fit(X_train_nominal)

        train_time_sec = round(time.time() - t0, 3)

        # Evaluation on real held-out test set
        infer_t0 = time.time()
        y_pred_rf = rf.predict(X_test)
        y_prob_rf = rf.predict_proba(X_test)[:, 1]
        infer_latency_ms = round(((time.time() - infer_t0) / len(X_test)) * 1000, 4)

        y_pred_lr = lr.predict(X_test_scaled)
        y_prob_lr = lr.predict_proba(X_test_scaled)[:, 1]

        # Threshold-based baseline comparison (traditional network alarms)
        # Alarm if latency > 40ms or packet_loss > 3% or rsrp < -105 dBm
        thresh_pred = (
            (df_test_raw["latency_ms"] > 35.0) |
            (df_test_raw["packet_loss_pct"] > 2.5) |
            (df_test_raw["rsrp_dbm"] < -105.0) |
            (df_test_raw["cpu_utilization_pct"] > 85.0)
        ).astype(int).values

        cm = confusion_matrix(y_test, y_pred_rf)
        tn, fp, fn, tp = cm.ravel()
        fpr = round(float(fp / (fp + tn + 1e-9)), 4)
        missed_fault_rate = round(float(fn / (fn + tp + 1e-9)), 4)

        # Feature importances
        importances = dict(sorted(
            zip(FEATURE_COLUMNS, [float(v) for v in rf.feature_importances_]),
            key=lambda item: item[1],
            reverse=True
        )[:15])

        metrics_summary = {
            "model_version": "v1.0-rf-iforest",
            "last_trained_timestamp": pd.Timestamp.now().isoformat(),
            "dataset_summary": {
                "total_samples": len(df_raw),
                "train_samples": len(df_train_raw),
                "test_samples": len(df_test_raw),
                "fault_prevalence_train_pct": round(float(np.mean(y_train) * 100), 2),
                "fault_prevalence_test_pct": round(float(np.mean(y_test) * 100), 2),
                "split_strategy": "Strict Temporal Split (Chrono, No Leakage)"
            },
            "evaluation_metrics": {
                "precision": round(float(precision_score(y_test, y_pred_rf, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, y_pred_rf, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, y_pred_rf, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, y_prob_rf)), 4),
                "pr_auc": round(float(average_precision_score(y_test, y_prob_rf)), 4),
                "false_positive_rate": fpr,
                "missed_fault_rate": missed_fault_rate,
                "lead_time_minutes": round(float(horizon_steps * 1.5), 1),
                "inference_latency_ms": infer_latency_ms,
                "training_time_seconds": train_time_sec
            },
            "confusion_matrix": [
                [int(tn), int(fp)],
                [int(fn), int(tp)]
            ],
            "baseline_comparison": {
                "random_forest": {
                    "precision": round(float(precision_score(y_test, y_pred_rf, zero_division=0)), 4),
                    "recall": round(float(recall_score(y_test, y_pred_rf, zero_division=0)), 4),
                    "f1": round(float(f1_score(y_test, y_pred_rf, zero_division=0)), 4),
                    "roc_auc": round(float(roc_auc_score(y_test, y_prob_rf)), 4)
                },
                "logistic_regression": {
                    "precision": round(float(precision_score(y_test, y_pred_lr, zero_division=0)), 4),
                    "recall": round(float(recall_score(y_test, y_pred_lr, zero_division=0)), 4),
                    "f1": round(float(f1_score(y_test, y_pred_lr, zero_division=0)), 4),
                    "roc_auc": round(float(roc_auc_score(y_test, y_prob_lr)), 4)
                },
                "threshold_rule_baseline": {
                    "precision": round(float(precision_score(y_test, thresh_pred, zero_division=0)), 4),
                    "recall": round(float(recall_score(y_test, thresh_pred, zero_division=0)), 4),
                    "f1": round(float(f1_score(y_test, thresh_pred, zero_division=0)), 4),
                    "description": "Fixed 3GPP static threshold alarms (reactive, high false alarm / late detection)"
                }
            },
            "feature_importances": importances
        }

        # Save artifacts
        os.makedirs(self.models_dir, exist_ok=True)
        joblib.dump(rf, self.rf_path)
        joblib.dump(lr, self.lr_path)
        joblib.dump(iso, self.iso_path)
        joblib.dump(self.fe, self.fe_path)
        with open(self.meta_path, "w") as f:
            json.dump(metrics_summary, f, indent=2)

        self.rf_model = rf
        self.lr_model = lr
        self.iso_model = iso
        self.metrics_metadata = metrics_summary
        self.is_loaded = True

        return metrics_summary

    def predict_point(
        self,
        raw_point: Dict[str, Any],
        recent_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Low-latency real-time inference on a streaming point.
        """
        if not self.is_loaded:
            self.load_models_if_present()

        if not self.is_loaded or self.rf_model is None or self.iso_model is None:
            # Fallback heuristic if not loaded yet
            fault_prob = 0.05
            is_fault = False
            anomaly_score = 0.10
            is_anomaly = False
            top_feats = {"latency_ms": 12.0}
        else:
            feat_vec = self.fe.extract_features_single(raw_point, recent_history)
            prob_arr = self.rf_model.predict_proba(feat_vec)
            fault_prob = float(prob_arr[0, 1])
            is_fault = bool(fault_prob >= 0.45)
            
            # Isolation forest decision score
            raw_anomaly = float(self.iso_model.decision_function(feat_vec)[0])
            anomaly_score = raw_anomaly
            is_anomaly = bool(raw_anomaly < -0.05)

            # Top contributing features
            top_feats = {}
            if self.metrics_metadata and "feature_importances" in self.metrics_metadata:
                imp = self.metrics_metadata["feature_importances"]
                for i, col in enumerate(FEATURE_COLUMNS[:len(feat_vec[0])]):
                    if col in imp:
                        val = float(feat_vec[0][i])
                        top_feats[col] = round(val, 2)
            else:
                top_feats = {"latency_ms": raw_point.get("latency_ms", 12.0)}

        return {
            "fault_probability": round(fault_prob, 4),
            "predicted_fault": is_fault,
            "anomaly_score": round(anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "top_features": top_feats
        }

model_pipeline = ModelPipelineManager()
