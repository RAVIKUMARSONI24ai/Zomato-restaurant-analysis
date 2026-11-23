"""
Data loader module for Zomato Restaurant Analysis.
Provides clean and reusable interfaces to read raw and processed datasets.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

DEFAULT_RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "zomato.csv"
DEFAULT_PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "zomato_cleaned.csv"


def load_raw_data(filepath: Optional[Path | str] = None) -> pd.DataFrame:
    """Loads the raw Zomato dataset."""
    path = Path(filepath) if filepath else DEFAULT_RAW_PATH
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {path}")
    return pd.read_csv(path)


def load_clean_data(filepath: Optional[Path | str] = None) -> pd.DataFrame:
    """Loads the processed/cleaned Zomato dataset."""
    path = Path(filepath) if filepath else DEFAULT_PROCESSED_PATH
    if not path.exists():
        raise FileNotFoundError(f"Cleaned data file not found at: {path}. Run data cleaning first.")
    return pd.read_csv(path)


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates a concise summary of the dataframe structure and missingness."""
    return {
        "total_records": len(df),
        "total_features": df.shape[1],
        "columns": list(df.columns),
        "missing_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }
