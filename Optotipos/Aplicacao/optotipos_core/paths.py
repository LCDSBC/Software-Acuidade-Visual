from __future__ import annotations

import os
import sys
from pathlib import Path


REQUIRED_DIRECTORIES = (
    "Configuracoes",
    "Perfis",
    "Testes",
    "Dados",
    "Backup",
    "Logs",
)


def portable_root() -> Path:
    """Return the folder that stores executables, settings and profiles.

    The packaged Windows executables are expected to live in ``Optotipos/``.
    During source execution the configurator may be launched from the sibling
    ``Configurador/`` folder, so this resolver deliberately supports both
    layouts while keeping all saved data under ``Optotipos/``.
    """

    env_root = os.environ.get("OPTOTIPOS_HOME")
    if env_root:
        return Path(env_root).expanduser().resolve()

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        if exe_dir.name.lower() == "configurador":
            sibling = exe_dir.parent / "Optotipos"
            if sibling.exists():
                return sibling.resolve()
        return exe_dir

    candidates: list[Path] = []
    if sys.argv and sys.argv[0]:
        candidates.append(Path(sys.argv[0]).resolve().parent)
    candidates.append(Path.cwd().resolve())

    for candidate in candidates:
        if candidate.name.lower() == "optotipos":
            return candidate
        sibling = candidate.parent / "Optotipos"
        if sibling.exists():
            return sibling.resolve()
        for parent in candidate.parents:
            if parent.name.lower() == "optotipos":
                return parent
            sibling = parent / "Optotipos"
            if sibling.exists():
                return sibling.resolve()

    return (Path.cwd() / "Optotipos").resolve()


def ensure_portable_tree(root: Path | None = None) -> Path:
    root = root or portable_root()
    root.mkdir(parents=True, exist_ok=True)
    for directory in REQUIRED_DIRECTORIES:
        (root / directory).mkdir(parents=True, exist_ok=True)
    return root


def config_path(name: str, root: Path | None = None) -> Path:
    return ensure_portable_tree(root) / "Configuracoes" / name


def profile_path(name: str, root: Path | None = None) -> Path:
    safe = "".join(ch for ch in name.strip() if ch.isalnum() or ch in ("-", "_", " ")).strip()
    if not safe:
        safe = "Perfil"
    if not safe.lower().endswith(".ini"):
        safe = f"{safe}.ini"
    return ensure_portable_tree(root) / "Perfis" / safe


def log_path(name: str, root: Path | None = None) -> Path:
    return ensure_portable_tree(root) / "Logs" / name
