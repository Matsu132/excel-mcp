from pathlib import Path

import pytest

from excel_mcp.infrastructure import SecurityError, Workspace


def test_workspace_rejects_escape(tmp_path: Path):
    ws = Workspace(str(tmp_path))
    with pytest.raises(SecurityError):
        ws.resolve("../secret.xlsx")


def test_workspace_rejects_non_xlsx(tmp_path: Path):
    with pytest.raises(SecurityError):
        Workspace(str(tmp_path)).resolve("book.xls")


def test_workspace_rejects_macro_extension(tmp_path: Path):
    with pytest.raises(SecurityError):
        Workspace(str(tmp_path)).resolve("book.xlsm")


def test_workspace_rejects_symlink(tmp_path: Path):
    target = tmp_path / "target.xlsx"
    target.touch()
    link = tmp_path / "link.xlsx"
    link.symlink_to(target)
    with pytest.raises(SecurityError):
        Workspace(str(tmp_path)).resolve("link.xlsx")
