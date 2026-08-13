from typing import Any
from pydantic import BaseModel, Field

class WorkbookRequest(BaseModel):
    path: str
    sheet: str | None = None

class ReadRequest(WorkbookRequest):
    range: str | None = None
    max_rows: int = Field(default=1000, ge=1, le=10000)

class WritePreviewRequest(WorkbookRequest):
    sheet: str
    cell: str | None = None
    range: str | None = None
    values: list[list[Any]]

class Preview(BaseModel):
    preview_id: str
    path: str
    sheet: str
    cell: str | None = None
    range: str | None = None
    values: list[list[Any]]
    sha256: str

