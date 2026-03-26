<<<<<<< HEAD
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
import pandas as pd
import numpy as np  # ✅ Fix: was missing — caused the NameError
import os

app = FastAPI()

# Global variable to store uploaded data
df_global = None


# 🔹 Home API
@app.get("/")
def home():
    return {"message": "FastAPI CSV Data API is running"}


# 🔹 Helper: clean a dataframe safely
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Replace inf/-inf with NaN, then NaN with None (JSON-safe)."""
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.where(pd.notnull(df), None)
    return df


# 🔹 Upload CSV
@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    global df_global

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        df = pd.read_csv(file.file)
        df = clean_dataframe(df)  # ✅ Use shared helper
        df_global = df

        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head().to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse CSV: {e}")


# 🔹 Get Full Data
@app.get("/get-all-data/")
def get_all_data():
    if df_global is None:
        raise HTTPException(status_code=400, detail="No CSV uploaded yet")

    return {
        "rows": len(df_global),
        "data": df_global.to_dict(orient="records")
    }


# 🔹 Get Specific Row
@app.get("/get-row/")
def get_row(index: int = Query(..., description="Row index (0-based)")):
    if df_global is None:
        raise HTTPException(status_code=400, detail="No CSV uploaded yet")

    # ✅ Fix: also guard against negative indexes
    if index < 0 or index >= len(df_global):
        raise HTTPException(
            status_code=400,
            detail=f"Index out of range. Valid range: 0 to {len(df_global) - 1}"
        )

    return df_global.iloc[index].to_dict()


# 🔹 Get Specific Column
@app.get("/get-column/")
def get_column(column: str = Query(..., description="Column name")):
    if df_global is None:
        raise HTTPException(status_code=400, detail="No CSV uploaded yet")

    if column not in df_global.columns:
        raise HTTPException(
            status_code=404,  # ✅ Fix: 404 is more accurate than 400 for "not found"
            detail=f"Column '{column}' not found. Available: {list(df_global.columns)}"
        )

    return {
        "column": column,
        "data": df_global[column].tolist()
    }


# 🔹 Filter Data
@app.get("/filter-data/")
def filter_data(
    column: str = Query(..., description="Column to filter on"),
    value: str = Query(..., description="Value to match")
):
    if df_global is None:
        raise HTTPException(status_code=400, detail="No CSV uploaded yet")

    if column not in df_global.columns:
        raise HTTPException(
            status_code=404,
            detail=f"Column '{column}' not found. Available: {list(df_global.columns)}"
        )

    filtered_df = df_global[df_global[column].astype(str) == value]

    # ✅ Fix: return a clear message when no rows match, instead of empty data
    if filtered_df.empty:
        return {"rows": 0, "message": f"No rows found where '{column}' = '{value}'", "data": []}

    return {
        "rows": len(filtered_df),
        "data": filtered_df.to_dict(orient="records")
    }


# 🔹 Read CSV from File
@app.get("/read-csv/")
def read_csv():
    filepath = "students_complete.csv"

    # ✅ Fix: check file exists before reading
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File '{filepath}' not found on server")

    try:
        df = pd.read_csv(filepath)
        df = clean_dataframe(df)  # ✅ Fix: uses helper instead of bare np calls

        return {
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.head().to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
=======
from fastapi import FastAPI, HTTPException, Query
from services.data_service import DataService
from models.student_model import Student

app = FastAPI()

data_service = DataService(r"services\students_complete.csv")

# ✅ GET all data
@app.get("/data")
def get_data():
    df = data_service.get_all()

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data found")

    return df.to_dict(orient="records")


# ✅ GET by ID
@app.get("/data/{student_id}", response_model=Student)
def get_student(student_id: str):
    result = data_service.get_by_student_id(student_id)

    if result.empty:
        raise HTTPException(status_code=404, detail="Record not found")

    return Student(**result.to_dict(orient="records")[0])


# ✅ FILTER (exact match)
@app.get("/filter/")
def filter_data(column: str, value: str):
    try:
        result = data_service.filter_data(column, value)

        if result.empty:
            return {"message": "No matching records"}

        return result.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ SEARCH (contains keyword)
@app.get("/search/")
def search_data(column: str, keyword: str):
    try:
        result = data_service.search_data(column, keyword)

        if result.empty:
            return {"message": "No matching records"}

        return result.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ PAGINATION
@app.get("/data_paginated/")
def get_paginated(page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    df = data_service.get_all()

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": len(df),
        "data": df.iloc[start:end].to_dict(orient="records")
    }
>>>>>>> 87e0fbab (third commit)
