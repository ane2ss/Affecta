import pandas as pd
from fastapi import UploadFile, HTTPException
import io

def read_excel_file(file: UploadFile) -> pd.DataFrame:
    """
    Reads an uploaded Excel file into a pandas DataFrame.
    """
    try:
        contents = file.file.read()
        # Use openpyxl engine for xlsx
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")

def normalize_text(text: str) -> str:
    """
    Normalizes text: uppercase and stripped.
    """
    if not isinstance(text, str):
        return str(text).strip().upper() if text is not None else ""
    return text.strip().upper()
