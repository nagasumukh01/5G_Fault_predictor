import os
import sys
from pathlib import Path
import pandas as pd

# Add repo root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.simulator.generator import NetworkTelemetrySimulator
from backend.app.ml.pipeline import model_pipeline
from backend.app.core.config import settings

def main():
    print("=" * 60)
    print("AI-Powered Fault Prediction in 5G Testbed - Model Trainer")
    print("Team: Team Dynamites")
    print("=" * 60)

    # 1. Generate realistic dataset with strict temporal structure
    print("[1/3] Generating synthetic 5G telemetry dataset with 8 scenarios...")
    sim = NetworkTelemetrySimulator(seed=1337)
    # Generate 1500 time steps across 3 sites, 3 cells, 5 components = 67,500 points
    # Let's generate a balanced rich sequence (e.g. 500 steps x 3 sites x 3 cells x 2 key components = 9,000 points)
    # For training speed + depth: 400 steps
    batch = sim.generate_batch(
        num_steps=350,
        step_interval_seconds=10,
        inject_fault_probability=0.07
    )
    df = pd.DataFrame(batch)
    
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    dataset_path = settings.DATA_DIR / "5g_synthetic_telemetry.csv"
    df.to_csv(dataset_path, index=False)
    print(f"Generated {len(df)} 5G telemetry records saved to: {dataset_path}")
    print(f"Columns: {list(df.columns)}")
    print(f"Class distribution for future_fault_within_horizon:")
    print(df["future_fault_within_horizon"].value_counts(normalize=True))

    # 2. Train and evaluate models
    print("\n[2/3] Training Random Forest, Logistic Regression, & Isolation Forest...")
    metrics = model_pipeline.train_and_persist(
        df_raw=df,
        horizon_steps=settings.HORIZON_STEPS,
        test_ratio=0.20
    )

    print("\n[3/3] Training Complete! Evaluation Results:")
    eval_m = metrics["evaluation_metrics"]
    print(f"  Precision:           {eval_m['precision']:.4f}")
    print(f"  Recall:              {eval_m['recall']:.4f}")
    print(f"  F1-Score:            {eval_m['f1_score']:.4f}")
    print(f"  ROC-AUC:             {eval_m['roc_auc']:.4f}")
    print(f"  PR-AUC:              {eval_m['pr_auc']:.4f}")
    print(f"  False Positive Rate: {eval_m['false_positive_rate']:.4f}")
    print(f"  Missed Fault Rate:   {eval_m['missed_fault_rate']:.4f}")
    print(f"  Inference Latency:   {eval_m['inference_latency_ms']} ms/sample")
    print(f"  Training Time:       {eval_m['training_time_seconds']} sec")
    print("\nConfusion Matrix [TN, FP], [FN, TP]:")
    print(metrics["confusion_matrix"])

    print("\nBaseline Comparison:")
    for model_k, model_v in metrics["baseline_comparison"].items():
        print(f"  {model_k}: {model_v}")

    print("\nTop Contributing Features:")
    for feat, imp in list(metrics["feature_importances"].items())[:6]:
        print(f"  - {feat}: {imp:.4f}")

    print("\nArtifacts successfully persisted to:", settings.ARTIFACTS_DIR)

if __name__ == "__main__":
    main()
