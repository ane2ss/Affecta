import json
import os
from typing import List, Dict
from models.schemas import AffectationItem
from utils.excel_utils import normalize_text

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/affectations.json")

class AffectationService:
    def __init__(self):
        self._ensure_data_file()
        self.affectations: List[Dict[str, str]] = self._load_data()

    def _ensure_data_file(self):
        """Creates the data directory and file if they don't exist."""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_data(self) -> List[Dict[str, str]]:
        """Loads affectations from JSON file."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self):
        """Saves current affectations to JSON file."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.affectations, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[AffectationItem]:
        return [AffectationItem(**item) for item in self.affectations]

    def add_or_update(self, item: AffectationItem):
        """Adds a new affectation or updates existing one based on normalized name."""
        norm_name = normalize_text(item.name)
        
        # Check if exists
        found = False
        for existing in self.affectations:
            if normalize_text(existing["name"]) == norm_name:
                existing["name"] = item.name # Update display name if needed, or keep original
                existing["commune"] = item.commune
                found = True
                break
        
        if not found:
            self.affectations.append(item.dict())
        
        self._save_data()

    def delete(self, name: str):
        """Deletes an affectation by name."""
        norm_name = normalize_text(name)
        self.affectations = [
            item for item in self.affectations 
            if normalize_text(item["name"]) != norm_name
        ]
        self._save_data()

    def bulk_import(self, items: List[AffectationItem]):
        """Replaces or merges bulk items. Here we merge/overwrite."""
        for item in items:
            self.add_or_update(item)

    def delete_all(self):
        """Deletes all affectations."""
        self.affectations = []
        self._save_data()

    def bulk_delete(self, names: List[str]):
        """Deletes multiple affectations by name."""
        norm_names = {normalize_text(n) for n in names}
        self.affectations = [
            item for item in self.affectations 
            if normalize_text(item["name"]) not in norm_names
        ]
        self._save_data()

    def bulk_update(self, names: List[str], new_commune: str):
        """Updates the commune for multiple affectations."""
        norm_names = {normalize_text(n) for n in names}
        for item in self.affectations:
            if normalize_text(item["name"]) in norm_names:
                item["commune"] = new_commune
        self._save_data()

    def export_data(self) -> str:
        """Exports affectations to an Excel file and returns the path."""
        df = pd.DataFrame(self.affectations)
        # Rename columns to match import format
        df = df.rename(columns={"name": "Nom majuscule", "commune": "Commune"})
        
        export_path = os.path.join(os.path.dirname(DATA_FILE), "affectations_export.xlsx")
        df.to_excel(export_path, index=False, engine='openpyxl')
        return export_path

    def get_mapping_dict(self) -> Dict[str, str]:
        """Returns a dictionary {NormalizedName: Commune} for fast lookups."""
        return {normalize_text(item["name"]): item["commune"] for item in self.affectations}

affectation_service = AffectationService()
