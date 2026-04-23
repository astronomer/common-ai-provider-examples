from __future__ import annotations

from pathlib import Path

from airflow.providers.standard.hooks.filesystem import FSHook


class FixturesHook(FSHook):
    """FSHook extended with list/read methods so agents can discover files."""

    def list_files(self, subdir: str = "") -> list[str]:
        root = Path(self.get_path())
        target = (root / subdir).resolve()
        if not str(target).startswith(str(root.resolve())):
            raise ValueError(f"subdir {subdir!r} escapes the fixtures root")
        if not target.exists():
            return []
        return sorted(
            str(p.relative_to(root)) for p in target.rglob("*") if p.is_file()
        )

    def read_file(self, relative_path: str, max_bytes: int = 65536) -> str:
        root = Path(self.get_path())
        target = (root / relative_path).resolve()
        if not str(target).startswith(str(root.resolve())):
            raise ValueError(f"path {relative_path!r} escapes the fixtures root")
        return target.read_text()[:max_bytes]
