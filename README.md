# Affecta ![Affecta Logo](https://link-to-your-image.com/logo.png)

Affecta is a local web application designed for finance teams to split large Excel files into multiple smaller files based on "Commune" using an editable mapping.

## Features
- **Modern UI**: Clean, professional interface with sidebar navigation.
- **Affectation Management**: 
    - Upload, add, edit, and delete mappings (Agent Name -> Commune).
    - **Search/Filter**: Quickly find agents or communes in the list.
- **Automated Splitting**: 
    - Upload a main Excel file.
    - **Filter Generation**: Select specific communes to generate files for.
    - Automatically generate one file per selected Commune.
    - Download results as a ZIP archive.
- **Local & Secure**: Runs entirely on your machine. No internet required. No database required.

## Installation

1. **Prerequisites**:
   - Python 3.11+ installed.

2. **Setup**:
   Navigate to the project folder:
   ```bash
   cd affecta/backend
   ```

   Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the backend server:
   ```bash
   # From the affecta/backend directory
   uvicorn main:app --reload
   ```

2. Open your browser and go to:
   [http://localhost:8000](http://localhost:8000)

## Usage Guide

### 1. Gestion des Affectations
- Navigate to the "Gestion des Affectations" tab.
- **Import**: Upload an Excel file with columns `Nom majuscule` and `Commune`.
- **Edit**: Use the table to view current mappings. Use the search bar to filter.
- **Add**: Manually add new entries using the "+ Ajouter" button.

### 2. Traitement du Fichier Principal
- Navigate to the "Traitement Fichier" tab.
- **Upload**: Drag and drop your main Excel file (must contain `Nom majuscule Agent`).
- **Filter**: (Optional) Uncheck communes you don't want to generate files for.
- **Generate**: Click "Générer les fichiers".
- **Download**: Once processing is complete, click "Télécharger le ZIP".

## Project Structure
- `backend/`: Python FastAPI application.
- `backend/data/`: Stores the `affectations.json` database.
- `frontend/`: HTML/CSS/JS user interface.
