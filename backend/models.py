from pydantic import BaseModel
from typing import Optional, Dict, Any


class ScanRequest(BaseModel):
    base: Optional[str] = None
    head: Optional[str] = None
    report_name: Optional[str] = None
    verbose: bool = False


class ScanResponse(BaseModel):
    ok: bool
    exit_code: int
    report_path: str
    result: Dict[str, Any]