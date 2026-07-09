import os
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any

class ProfitPredictor:
    def __init__(self):
        # Determine paths dynamically based on app file structure
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "models", "profit_predection_model.pkl")
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads the trained pickle pipeline."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Trained profit model not found at {self.model_path}. "
                f"Please ensure your checkpoint/pickle file is correctly saved inside the models directory."
            )
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, input_data: Dict[str, Any]) -> float:
        """
        Accepts a dictionary of raw parameters, mirrors the feature expansion 
        and extraction logic from the Jupyter Notebook, and runs pipeline inference.
        """
        if self.model is None:
            raise RuntimeError("Model is not initialized or loaded.")

        # Convert incoming payload into a dataframe format matching the model's signature
        raw_df = pd.DataFrame([input_data])

        # Ensure datetime features are processed if provided as strings
        for date_col in ['Order Date', 'Ship Date']:
            if date_col in raw_df.columns and not pd.api.types.is_datetime64_any_dtype(raw_df[date_col]):
                raw_df[date_col] = pd.to_datetime(raw_df[date_col])

        # Feature Engineering: calendar table merge simulation logic
        # If the front-end doesn't pre-calculate these fields, extract them directly
        if 'Order Date' in raw_df.columns:
            raw_df['Order Year'] = raw_df['Order Date'].dt.year
            raw_df['Order Quarter'] = raw_df['Order Date'].dt.quarter
            raw_df['Order Month'] = raw_df['Order Date'].dt.strftime('%b')
            raw_df['Order Week'] = raw_df['Order Date'].dt.isocalendar().week.astype(int)
            raw_df['Order Day'] = raw_df['Order Date'].dt.strftime('%A')

        if 'Ship Date' in raw_df.columns:
            raw_df['Ship Year'] = raw_df['Ship Date'].dt.year
            raw_df['Ship Quarter'] = raw_df['Ship Date'].dt.quarter
            raw_df['Ship Month'] = raw_df['Ship Date'].dt.strftime('%b')
            raw_df['Ship Week'] = raw_df['Ship Date'].dt.isocalendar().week.astype(int)
            raw_df['Ship Day'] = raw_df['Ship Date'].dt.strftime('%A')

        # Run inference using the pre-configured sklearn Pipeline
        prediction = self.model.predict(raw_df)
        
        return float(prediction[0])

# Singleton instance for simple app dependency injection
profit_predictor = ProfitPredictor()