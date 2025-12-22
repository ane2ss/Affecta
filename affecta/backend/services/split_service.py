import pandas as pd
import os
import shutil
import zipfile
from typing import Optional
from services.affectation_service import affectation_service
from utils.excel_utils import normalize_text

TEMP_DIR = os.path.join(os.path.dirname(__file__), "../temp")

class SplitService:
    def __init__(self):
        os.makedirs(TEMP_DIR, exist_ok=True)

    def process_split(self, df: pd.DataFrame, target_communes: Optional[list[str]] = None) -> str:
        """
        Splits the dataframe by Commune and returns the path to the generated ZIP file.
        """
        # Clean up temp dir
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

        # Get mapping
        mapping = affectation_service.get_mapping_dict()

        # Normalize the key column in the main file
        # Check for "Nom majuscule Agent" or "Nom majuscule"
        agent_col = "Nom majuscule Agent"
        if agent_col not in df.columns:
            if "Nom majuscule" in df.columns:
                agent_col = "Nom majuscule"
            else:
                raise ValueError("Column 'Nom majuscule Agent' or 'Nom majuscule' not found in the uploaded file.")

        # Create a normalized column for mapping
        df["_normalized_name"] = df[agent_col].apply(normalize_text)

        # Map Commune
        df["Commune"] = df["_normalized_name"].map(mapping)

        # Handle unmatched
        df["Commune"] = df["Commune"].fillna("NON_AFFECTE")

        # Drop the helper column
        df = df.drop(columns=["_normalized_name"])
        
        print(f"Unique communes in data BEFORE filtering: {df['Commune'].unique()}")

        # Filter if target_communes provided
        if target_communes:
            print(f"Filtering for communes (Received): {target_communes}")
            # Normalize target communes for comparison just in case, or assume exact match
            # Let's assume exact match as they come from the UI which gets them from the backend
            df = df[df["Commune"].isin(target_communes)]
            print(f"Unique communes in data AFTER filtering: {df['Commune'].unique()}")

        if df.empty:
             print("DataFrame is empty after filtering!")
             raise ValueError("No data found for the selected communes.")

        # Group and Save
        generated_files = []
        grouped = df.groupby("Commune")
        
        print(f"Found {len(grouped)} groups.")

        for commune, group_df in grouped:
            # Sanitize filename
            safe_commune = "".join([c if c.isalnum() or c in (' ', '-', '_') else '_' for c in str(commune)]).strip()
            filename = f"{safe_commune}.xlsx"
            filepath = os.path.join(TEMP_DIR, filename)
            
            print(f"Generating {filepath} with {len(group_df)} rows.")
            
            # Save to Excel
            group_df.to_excel(filepath, index=False, engine='openpyxl')
            generated_files.append(filepath)

        if not generated_files:
             print("No files generated!")
             raise ValueError("No files were generated.")

        # Create ZIP
        zip_filename = "resultats_affecta.zip"
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        
        print(f"Creating ZIP at {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))
        
        print(f"ZIP created successfully at {zip_path}")

        return zip_path

split_service = SplitService()
