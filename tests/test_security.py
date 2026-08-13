from pathlib import Path
import pytest
from excel_mcp.infrastructure import SecurityError, Workspace

def test_workspace_rejects_escape(tmp_path: Path):
    ws=Workspace(str(tmp_path))
    with pytest.raises(SecurityError): ws.resolve("../secret.xlsx")

def test_workspace_rejects_non_xlsx(tmp_path: Path):
    with pytest.raises(SecurityError): Workspace(str(tmp_path)).resolve("book.xls")

