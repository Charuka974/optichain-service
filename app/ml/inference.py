import joblib
import pandas as pd
import os
from fastapi import HTTPException

MODEL_DIR = "model"

class MLModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_columns = None
        self.historical_rate_maps = None
        self.frequency_maps = None
        self.overall_late_rate = None
        self.outlier_bounds = None

    def load_model(self):
        try:
            self.model = joblib.load(os.path.join(MODEL_DIR, "late_delivery_model.pkl"))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
            self.model_columns = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))
            self.historical_rate_maps = joblib.load(os.path.join(MODEL_DIR, "historical_rate_maps.pkl"))
            self.frequency_maps = joblib.load(os.path.join(MODEL_DIR, "frequency_maps.pkl"))
            self.overall_late_rate = joblib.load(os.path.join(MODEL_DIR, "overall_late_rate.pkl"))
            self.outlier_bounds = joblib.load(os.path.join(MODEL_DIR, "outlier_bounds.pkl"))
            print("All ML models and preprocessing files loaded successfully.")
        except Exception as e:
            print(f"Failed to load ML files: {e}")

    def predict(self, input_data: dict) -> dict:
        if self.model is None:
            raise HTTPException(status_code=503, detail="Model is not loaded.")
        
        try:
            # 1. Load Data
            df = pd.DataFrame([input_data])
            
            # 2. Date Feature Engineering
            df["order date (DateOrders)"] = pd.to_datetime(df["order date (DateOrders)"], errors="coerce")
            df["order_dow"] = df["order date (DateOrders)"].dt.dayofweek
            df["order_month"] = df["order date (DateOrders)"].dt.month
            df["order_is_weekend"] = df["order_dow"].isin([5, 6]).astype(int)
            df = df.drop(columns=["order date (DateOrders)"])

            # 3. Historical Late-Delivery Rate
            group_cols = ["Customer Segment", "Order Region", "Shipping Mode"]
            for col in group_cols:
                rate_lookup = self.historical_rate_maps.get(col, {})
                df[f"{col}_late_rate"] = df[col].map(rate_lookup).fillna(self.overall_late_rate)

            # 4. Outlier Handling
            outlier_cols = ["Sales", "Order Item Quantity", "Order Item Product Price", "Order Item Discount"]
            for col in outlier_cols:
                lower, upper = self.outlier_bounds.get(col, (0, 0))
                df[col] = df[col].clip(lower, upper)

            # 5. Feature Interaction
            df["mode_region_interaction"] = df["Shipping Mode"].astype(str) + "_" + df["Order Region"].astype(str)
            df["qty_x_discount_rate"] = df["Order Item Quantity"] * df["Order Item Discount Rate"]

            # 6. Frequency Encoding
            high_cardinality_cols = [
                "Customer City", "Customer Country", "Customer State",
                "Order City", "Order Country", "Order State",
                "Department Name", "mode_region_interaction", "Order Status"
            ]
            for col in high_cardinality_cols:
                freq_lookup = self.frequency_maps.get(col, {})
                df[col + "_freq"] = df[col].map(freq_lookup).fillna(0)
            df = df.drop(columns=high_cardinality_cols)

            # 7. One-Hot Encoding
            low_cardinality_cols = ["Type", "Customer Segment", "Shipping Mode", "Market", "Order Region", "Category Name"]
            df = pd.get_dummies(df, columns=low_cardinality_cols)

            # 8. Drop Text & Reindex to Match Training Columns Exactly
            leftover_text_cols = df.select_dtypes(include=["object"]).columns.tolist()
            df = df.drop(columns=leftover_text_cols)
            df = df.reindex(columns=self.model_columns, fill_value=0)

            # 9. Scale Numeric Columns
            scale_cols = ["Sales", "Order Item Quantity", "Order Item Product Price",
                          "Order Item Discount", "Order Item Discount Rate",
                          "Sales per customer", "Order Item Total"]
            df[scale_cols] = self.scaler.transform(df[scale_cols])

            # 10. Predict
            prediction = self.model.predict(df)[0]
            probability = self.model.predict_proba(df)[0][1] if hasattr(self.model, "predict_proba") else float(prediction)
            
            return {
                "delayed": int(prediction),
                "delay_probability": float(probability),
                "status": "Success"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Prediction formatting error: {str(e)}")

ml_service = MLModel()