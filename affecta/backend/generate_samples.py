import pandas as pd
import os

# Define paths
desktop_path = "/home/aness/Desktop/Affecta"
affectation_path = os.path.join(desktop_path, "sample_affectations.xlsx")
main_file_path = os.path.join(desktop_path, "sample_main_file.xlsx")

# 1. Create Sample Affectations
affectations_data = {
    "Nom majuscule": ["AGENT ONE", "AGENT TWO", "AGENT THREE", "AGENT FOUR", "AGENT FIVE"],
    "Commune": ["ALGER CENTRE", "ORAN", "CONSTANTINE", "ALGER CENTRE", "ORAN"]
}
df_aff = pd.DataFrame(affectations_data)
df_aff.to_excel(affectation_path, index=False)
print(f"Created {affectation_path}")

# 2. Create Sample Main File
main_data = {
    "ID agent": [101, 102, 103, 104, 105],
    "Nom majuscule Agent": ["AGENT ONE", "AGENT TWO", "AGENT THREE", "AGENT FOUR", "AGENT FIVE"],
    "Wilaya": ["16", "31", "25", "16", "31"],
    "Statut": ["Actif", "Actif", "Actif", "Actif", "Inactif"],
    "HT": [1000, 2000, 1500, 1200, 2200],
    "TVA": [190, 380, 285, 228, 418],
    "TTC": [1190, 2380, 1785, 1428, 2618]
}
df_main = pd.DataFrame(main_data)
df_main.to_excel(main_file_path, index=False)
print(f"Created {main_file_path}")
