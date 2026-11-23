"""
Machine Learning Module for Zomato Restaurant Rating Prediction.
Trains a model to predict restaurant ratings and identifies key success drivers.
"""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


class RestaurantRatingPredictor:
    """Predicts restaurant rating and computes feature importance drivers."""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        self.feature_columns = []
        self.top_locations = []
        self.top_rest_types = []
        self.metrics = {}
        self.feature_importance_df = pd.DataFrame()
        self.is_trained = False

    def _prepare_features(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        data = pd.DataFrame()
        data["cost_for_two"] = pd.to_numeric(df["cost_for_two"], errors="coerce").fillna(600)
        data["online_order"] = (df["online_order"] == "Yes").astype(int)
        data["book_table"] = (df["book_table"] == "Yes").astype(int)
        data["cuisine_count"] = pd.to_numeric(df.get("cuisine_count", 2), errors="coerce").fillna(2)
        
        # Categorical handling: top categories one-hot encoded
        if is_training:
            self.top_locations = df["location"].value_counts().head(8).index.tolist()
            self.top_rest_types = df["rest_type"].value_counts().head(6).index.tolist()
            
        for loc in self.top_locations:
            data[f"loc_{loc}"] = (df["location"] == loc).astype(int)
            
        for rtype in self.top_rest_types:
            data[f"type_{rtype}"] = (df["rest_type"] == rtype).astype(int)
            
        if is_training:
            self.feature_columns = list(data.columns)
        else:
            # Reindex to ensure identical columns in inference
            for col in self.feature_columns:
                if col not in data.columns:
                    data[col] = 0
            data = data[self.feature_columns]
            
        return data

    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Trains the Random Forest model and records performance metrics."""
        # Train on records with actual ratings
        rated_mask = df["rating"].notna()
        train_df = df[rated_mask].copy()
        
        X = self._prepare_features(train_df, is_training=True)
        y = train_df["rating"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        
        # Feature importances
        importances = self.model.feature_importances_
        fi_df = pd.DataFrame({
            "Feature": self.feature_columns,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False).reset_index(drop=True)
        
        # Make feature names human-friendly
        clean_names = {
            "book_table": "Table Booking Enabled",
            "cost_for_two": "Approx Cost for Two",
            "cuisine_count": "Cuisine Diversity",
            "online_order": "Online Ordering Enabled"
        }
        fi_df["Feature_Label"] = fi_df["Feature"].apply(
            lambda x: clean_names.get(x, x.replace("loc_", "Location: ").replace("type_", "Type: "))
        )
        
        self.feature_importance_df = fi_df
        self.metrics = {
            "MAE": round(mae, 3),
            "R2": round(r2, 3),
            "sample_size": len(train_df)
        }
        self.is_trained = True
        return self.metrics

    def predict(self, input_dict: Dict[str, Any]) -> Tuple[float, str]:
        """
        Predicts the expected rating for a single restaurant specification.
        Returns predicted rating and rating tier.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")
            
        temp_df = pd.DataFrame([input_dict])
        X = self._prepare_features(temp_df, is_training=False)
        pred_rating = float(self.model.predict(X)[0])
        pred_rating = round(np.clip(pred_rating, 1.0, 5.0), 2)
        
        if pred_rating >= 4.3:
            tier = "Exceptional (Top 10% on Platform)"
        elif pred_rating >= 3.9:
            tier = "High Performer (Above Average)"
        elif pred_rating >= 3.5:
            tier = "Moderate Performer (Average)"
        else:
            tier = "At-Risk (Needs Menu & Service Optimization)"
            
        return pred_rating, tier
