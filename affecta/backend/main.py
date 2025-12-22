from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import pandas as pd

from services.affectation_service import affectation_service
from services.split_service import split_service
from utils.excel_utils import read_excel_file
from models.schemas import AffectationItem, GenericResponse, AffectationListResponse

app = FastAPI(title="Affecta Local API")

# CORS (allow all for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (Frontend)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# --- Affectation Endpoints ---

@app.get("/api/affectations", response_model=AffectationListResponse)
async def get_affectations():
    items = affectation_service.get_all()
    return {"items": items, "count": len(items)}

@app.post("/api/affectations/add", response_model=GenericResponse)
async def add_affectation(item: AffectationItem):
    affectation_service.add_or_update(item)
    return {"message": "Added successfully", "success": True}

@app.post("/api/affectations/upload", response_model=GenericResponse)
async def upload_affectations(file: UploadFile = File(...)):
    try:
        df = read_excel_file(file)
        
        # Validate columns
        required = ["Nom majuscule", "Commune"]
        if not all(col in df.columns for col in required):
            return JSONResponse(
                status_code=400, 
                content={"message": f"Missing columns. Required: {required}", "success": False}
            )
        
        items = []
        for _, row in df.iterrows():
            if pd.notna(row["Nom majuscule"]) and pd.notna(row["Commune"]):
                items.append(AffectationItem(
                    name=str(row["Nom majuscule"]),
                    commune=str(row["Commune"])
                ))
        
        affectation_service.bulk_import(items)
        return {"message": f"Imported {len(items)} entries", "success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e), "success": False})

@app.delete("/api/affectations/delete/{name}", response_model=GenericResponse)
async def delete_affectation(name: str):
    affectation_service.delete(name)
    return {"message": "Deleted successfully", "success": True}

@app.delete("/api/affectations/delete-all", response_model=GenericResponse)
async def delete_all_affectations():
    affectation_service.delete_all()
    return {"message": "All affectations deleted", "success": True}

@app.post("/api/affectations/bulk-delete", response_model=GenericResponse)
async def bulk_delete_affectations(names: List[str] = Body(...)):
    affectation_service.bulk_delete(names)
    return {"message": f"Deleted {len(names)} items", "success": True}

@app.post("/api/affectations/bulk-update", response_model=GenericResponse)
async def bulk_update_affectations(names: List[str] = Body(...), commune: str = Body(...)):
    affectation_service.bulk_update(names, commune)
    return {"message": f"Updated {len(names)} items", "success": True}

@app.get("/api/affectations/export")
async def export_affectations():
    path = affectation_service.export_data()
    return FileResponse(path, filename="affectations_export.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Main File Processing Endpoints ---

@app.post("/api/generate")
async def generate_files(
    file: UploadFile = File(...),
    communes: str = Body(None) # Comma separated string or JSON string
):
    try:
        df = read_excel_file(file)
        
        target_communes = None
        if communes:
            # Simple comma separation
            target_communes = [c.strip() for c in communes.split(",") if c.strip()]
        
        zip_path = split_service.process_split(df, target_communes)
        return {"message": "Files generated", "success": True, "download_url": "/api/download/zip"}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"message": str(ve), "success": False})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e), "success": False})

@app.get("/api/download/zip")
async def download_zip():
    zip_path = os.path.join(os.path.dirname(__file__), "temp/resultats_affecta.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP file not found. Please generate it first.")
    return FileResponse(zip_path, filename="resultats_affecta.zip", media_type="application/zip")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
