import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

CORE_NUMERIC_FEATURES = [
    "rsrp_dbm",
    "rsrq_db",
    "sinr_db",
    "latency_ms",
    "packet_loss_pct",
    "throughput_mbps",
    "connected_users",
    "prb_utilization_pct",
    "cpu_utilization_pct",
    "memory_utilization_pct",
    "availability_pct"
]

FEATURE_COLUMNS = [
    # Raw features
    "rsrp_dbm",
    "rsrq_db",
    "sinr_db",
    "latency_ms",
    "packet_loss_pct",
    "throughput_mbps",
    "connected_users",
    "prb_utilization_pct",
    "cpu_utilization_pct",
    "memory_utilization_pct",
    "availability_pct",
    # Rolling stats
    "rsrp_rolling_mean_3",
    "sinr_rolling_mean_3",
    "latency_rolling_mean_3",
    "packet_loss_rolling_mean_3",
    "prb_rolling_mean_3",
    "cpu_rolling_mean_3",
    "latency_rolling_std_3",
    "throughput_rolling_std_3",
    # Lags
    "rsrp_lag_1",
    "sinr_lag_1",
    "latency_lag_1",
    "packet_loss_lag_1",
    "throughput_lag_1",
    "rsrp_lag_2",
    "latency_lag_2",
    # Deltas
    "delta_latency_1",
    "delta_throughput_1",
    "delta_sinr_1",
    # Domain interactions
    "spectral_efficiency_proxy",
    "load_stress_index",
    "channel_quality_deficit"
]

class FeatureEngineer:
    """
    Constructs high-order temporal, lag, rolling, and domain-specific 5G network features
    while strictly avoiding future target leakage.
    """
    def __init__(self):
        self.feature_columns = FEATURE_COLUMNS
        self.medians: Dict[str, float] = {}

    def extract_features_df(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        df = df.copy()
        orig_index = df.index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values(by=["site_id", "cell_id", "component_id", "timestamp"])

        # Group by site, cell, component to prevent cross-entity bleeding
        grouped = df.groupby(["site_id", "cell_id", "component_id"], group_keys=False)

        # Rolling statistics (historical only: min_periods=1)
        df["rsrp_rolling_mean_3"] = grouped["rsrp_dbm"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["sinr_rolling_mean_3"] = grouped["sinr_db"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["latency_rolling_mean_3"] = grouped["latency_ms"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["packet_loss_rolling_mean_3"] = grouped["packet_loss_pct"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["prb_rolling_mean_3"] = grouped["prb_utilization_pct"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["cpu_rolling_mean_3"] = grouped["cpu_utilization_pct"].apply(lambda s: s.rolling(3, min_periods=1).mean())
        df["latency_rolling_std_3"] = grouped["latency_ms"].apply(lambda s: s.rolling(3, min_periods=1).std().fillna(0.0))
        df["throughput_rolling_std_3"] = grouped["throughput_mbps"].apply(lambda s: s.rolling(3, min_periods=1).std().fillna(0.0))

        # Lags
        df["rsrp_lag_1"] = grouped["rsrp_dbm"].shift(1).bfill()
        df["sinr_lag_1"] = grouped["sinr_db"].shift(1).bfill()
        df["latency_lag_1"] = grouped["latency_ms"].shift(1).bfill()
        df["packet_loss_lag_1"] = grouped["packet_loss_pct"].shift(1).bfill()
        df["throughput_lag_1"] = grouped["throughput_mbps"].shift(1).bfill()
        df["rsrp_lag_2"] = grouped["rsrp_dbm"].shift(2).bfill()
        df["latency_lag_2"] = grouped["latency_ms"].shift(2).bfill()

        # Deltas
        df["delta_latency_1"] = df["latency_ms"] - df["latency_lag_1"]
        df["delta_throughput_1"] = df["throughput_mbps"] - df["throughput_lag_1"]
        df["delta_sinr_1"] = df["sinr_db"] - df["sinr_lag_1"]

        # Domain interactions
        df["spectral_efficiency_proxy"] = df["throughput_mbps"] / (df["prb_utilization_pct"] + 1e-4)
        df["load_stress_index"] = (df["prb_utilization_pct"] * 0.4) + (df["cpu_utilization_pct"] * 0.3) + (df["memory_utilization_pct"] * 0.3)
        df["channel_quality_deficit"] = np.maximum(0.0, -95.0 - df["rsrp_dbm"]) + np.maximum(0.0, 10.0 - df["sinr_db"])

        # Restore original index alignment
        df = df.loc[orig_index]

        # Fill any residual NaNs with medians
        if is_training:
            for col in self.feature_columns:
                self.medians[col] = float(df[col].median()) if col in df.columns else 0.0
        
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = self.medians.get(col, 0.0)
            else:
                df[col] = df[col].fillna(self.medians.get(col, 0.0))

        return df[self.feature_columns]

    def extract_features_single(self, raw_point: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> np.ndarray:
        """
        Featurize a single incoming telemetry point using optional recent history buffer.
        """
        history = history or []
        all_points = history[-4:] + [raw_point]
        df_temp = pd.DataFrame(all_points)
        for col in CORE_NUMERIC_FEATURES:
            if col not in df_temp.columns:
                df_temp[col] = raw_point.get(col, 0.0)
            df_temp[col] = pd.to_numeric(df_temp[col], errors="coerce").fillna(0.0)
        
        if "site_id" not in df_temp.columns:
            df_temp["site_id"] = raw_point.get("site_id", "SITE-01")
        if "cell_id" not in df_temp.columns:
            df_temp["cell_id"] = raw_point.get("cell_id", "CELL-01")
        if "component_id" not in df_temp.columns:
            df_temp["component_id"] = raw_point.get("component_id", "gNodeB-CU")

        feat_df = self.extract_features_df(df_temp, is_training=False)
        return feat_df.iloc[[-1]].values
