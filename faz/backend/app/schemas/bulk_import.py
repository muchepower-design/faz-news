# app/schemas/bulk_import.py
from pydantic import BaseModel
from typing import Optional

class BulkImportResponse(BaseModel):
    success: bool
    rows_imported: int
    errors: Optional[str] = None