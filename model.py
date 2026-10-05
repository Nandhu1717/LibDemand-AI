import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class BookDemandModel:
    """
    Random Forest Regression model pipeline for Library Book Demand Prediction.
    Handles encoding, training, validation metrics, feature importance calculation,
    dynamic demand classification, and batch/single predictions.
    """

    def __init__(self, n_estimators: int = 100, max_depth: Optional[int] = 12, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        
        self.pipeline: Optional[Pipeline] = None
        self.is_trained: bool = False
        
        # Diagnostic Metrics
        self.metrics: Dict[str, Any] = {}
        self.feature_importances_df: Optional[pd.DataFrame] = None
        self.test_predictions_df: Optional[pd.DataFrame] = None
        
        # Dynamic Classification Thresholds
        self.threshold_low: float = 80.0
        self.threshold_high: float = 160.0
        self.threshold_mode: str = "quantile"  # "quantile" or "custom"
        self.threshold_explanation: str = ""

    def fit_and_evaluate(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        threshold_mode: str = "quantile",
        custom_low: float = 80.0,
        custom_high: float = 160.0
    ) -> Dict[str, Any]:
        """
        Trains the Random Forest Regression model on the dataset using a proper train/test split.
        Computes evaluation metrics (MAE, RMSE, R2) and calculates dynamic demand classification thresholds.
        """
        if df.empty or len(df) < 5:
            raise ValueError("Insufficient data to train Machine Learning model. At least 5 rows are required.")

        feature_cols = [
            'book_category', 'month', 'semester',
            'number_of_students', 'previous_borrowing_count', 'previous_demand'
        ]
        target_col = 'demand'

        X = df[feature_cols]
        y = df[target_col]

        # Define preprocessing transformers to avoid data leakage
        categorical_cols = ['book_category']
        numerical_cols = ['month', 'semester', 'number_of_students', 'previous_borrowing_count', 'previous_demand']

        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
                ('num', 'passthrough', numerical_cols)
            ]
        )

        regressor = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )

        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])

        # Train / Test Split (Strict split before fitting to avoid data leakage)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )

        # Fit pipeline on training set
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        # Predict on test set for evaluation
        y_pred = self.pipeline.predict(X_test)
        y_pred_rounded = np.clip(np.round(y_pred), a_min=0, a_max=None)

        mae = mean_absolute_error(y_test, y_pred_rounded)
        mse = mean_squared_error(y_test, y_pred_rounded)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred_rounded)

        self.metrics = {
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'r2': round(float(r2), 4),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'total_samples': len(df)
        }

        # Save test set predictions for diagnostic plots
        self.test_predictions_df = pd.DataFrame({
            'Actual_Demand': y_test.values,
            'Predicted_Demand': y_pred_rounded,
            'Residual': y_test.values - y_pred_rounded
        }).reset_index(drop=True)

        # Calculate Feature Importances
        cat_encoder = self.pipeline.named_steps['preprocessor'].named_transformers_['cat']
        encoded_cat_names = list(cat_encoder.get_feature_names_out(categorical_cols))
        
        # Clean feature names for clean UI display
        clean_cat_names = [col.replace('book_category_', 'Category: ') for col in encoded_cat_names]
        feature_names = clean_cat_names + [
            'Month of Year', 'Semester', 'Enrolled Students',
            'Previous Borrowings', 'Previous Demand'
        ]

        importances = self.pipeline.named_steps['regressor'].feature_importances_

        self.feature_importances_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False).reset_index(drop=True)

        # Determine Classification Thresholds
        self.threshold_mode = threshold_mode
        if threshold_mode == "quantile":
            q33 = float(np.quantile(y, 0.33))
            q66 = float(np.quantile(y, 0.66))
            self.threshold_low = round(q33, 1)
            self.threshold_high = round(q66, 1)
            self.threshold_explanation = (
                f"Data-driven quantiles from historical circulation data: "
                f"Low (< {self.threshold_low} books), "
                f"Medium ({self.threshold_low} – {self.threshold_high} books), "
                f"High (> {self.threshold_high} books)."
            )
        else:
            self.threshold_low = float(custom_low)
            self.threshold_high = float(custom_high)
            self.threshold_explanation = (
                f"User-specified static thresholds: "
                f"Low (< {self.threshold_low} books), "
                f"Medium ({self.threshold_low} – {self.threshold_high} books), "
                f"High (> {self.threshold_high} books)."
            )

        return self.metrics

    def classify_demand(self, predicted_demand: float) -> str:
        """Classifies predicted demand value into Low, Medium, or High level."""
        if predicted_demand < self.threshold_low:
            return "Low"
        elif predicted_demand <= self.threshold_high:
            return "Medium"
        else:
            return "High"

    def predict_single(
        self,
        book_category: str,
        month: int,
        semester: int,
        number_of_students: int,
        previous_borrowing_count: int,
        previous_demand: int
    ) -> Dict[str, Any]:
        """Predicts demand for a single input record."""
        if not self.is_trained or self.pipeline is None:
            raise ValueError("Model has not been trained yet. Please train the model before making predictions.")

        input_df = pd.DataFrame([{
            'book_category': str(book_category),
            'month': int(month),
            'semester': int(semester),
            'number_of_students': int(number_of_students),
            'previous_borrowing_count': int(previous_borrowing_count),
            'previous_demand': int(previous_demand)
        }])

        raw_pred = self.pipeline.predict(input_df)[0]
        predicted_demand = int(round(max(0, raw_pred)))
        demand_level = self.classify_demand(predicted_demand)
        recommendation = self.get_inventory_recommendation(demand_level, book_category)

        return {
            'predicted_demand': predicted_demand,
            'demand_level': demand_level,
            'threshold_explanation': self.threshold_explanation,
            'recommendation': recommendation
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generates predictions and demand levels for a batch DataFrame."""
        if not self.is_trained or self.pipeline is None:
            raise ValueError("Model has not been trained yet. Please train the model before making batch predictions.")

        feature_cols = [
            'book_category', 'month', 'semester',
            'number_of_students', 'previous_borrowing_count', 'previous_demand'
        ]

        result_df = df.copy()
        raw_preds = self.pipeline.predict(df[feature_cols])
        rounded_preds = [int(round(max(0, val))) for val in raw_preds]
        
        result_df['Predicted_Demand'] = rounded_preds
        result_df['Demand_Level'] = [self.classify_demand(p) for p in rounded_preds]
        
        # Add recommended stock action column
        result_df['Stock_Action'] = result_df['Demand_Level'].map({
            'High': '🚨 Reorder & Restock Urgently',
            'Medium': '⚡ Maintain Regular Inventory',
            'Low': '🌱 Retain Existing Shelf Stock'
        })
        
        return result_df

    @staticmethod
    def get_inventory_recommendation(demand_level: str, category: str) -> Dict[str, str]:
        """Returns structured inventory stock recommendations for library staff."""
        if demand_level == "High":
            return {
                "badge": "🚨 HIGH DEMAND PRIORITY",
                "title": f"Increase Physical Stock for {category}",
                "detail": "High demand anticipated! Increase available shelf copies, place priority reorders with book vendors, and reserve digital copies for high-frequency circulation.",
                "color_class": "high",
                "bg_color": "#FEF2F2",
                "border_color": "#EF4444",
                "text_color": "#991B1B"
            }
        elif demand_level == "Medium":
            return {
                "badge": "⚡ BALANCED DEMAND",
                "title": f"Monitor Regular Circulation for {category}",
                "detail": "Moderate demand expected. Maintain standard shelf stock, monitor weekly borrowing trends, and keep reference desk reserves ready.",
                "color_class": "medium",
                "bg_color": "#FFFBEB",
                "border_color": "#F59E0B",
                "text_color": "#92400E"
            }
        else:
            return {
                "badge": "🌱 OPTIMAL INVENTORY",
                "title": f"Sufficient Stock for {category}",
                "detail": "Low demand expected. Current inventory is sufficient. Avoid ordering excess shelf inventory, reallocate unused shelf space, and monitor digital access.",
                "color_class": "low",
                "bg_color": "#ECFDF5",
                "border_color": "#10B981",
                "text_color": "#065F46"
            }
