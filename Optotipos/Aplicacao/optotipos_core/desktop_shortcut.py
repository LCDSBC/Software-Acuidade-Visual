from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


SHORTCUT_NAME = "Optótipos Profissional.lnk"


def desktop_folder() -> Path | None:
    if os.name != "nt":
        return None
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        return None
    return Path(user_profile) / "Desktop"


def executable_target(root: Path) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    candidate = root / "Optotipos.exe"
    if candidate.exists():
        return candidate.resolve()
    return (root / "Optotipos.pyw").resolve()


def ensure_desktop_shortcut(root: Path) -> Path | None:
    desktop = desktop_folder()
    if desktop is None:
        return None
    desktop.mkdir(parents=True, exist_ok=True)
    shortcut = desktop / SHORTCUT_NAME
    if shortcut.exists():
        return shortcut

    target = executable_target(root)
    powershell = shutil_which("powershell.exe") or shutil_which("powershell")
    if powershell:
        command = (
            "$WshShell = New-Object -comObject WScript.Shell; "
            f"$Shortcut = $WshShell.CreateShortcut('{shortcut}'); "
            f"$Shortcut.TargetPath = '{target}'; "
            f"$Shortcut.WorkingDirectory = '{root}'; "
            "$Shortcut.Save()"
        )
        subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command], check=False, timeout=10)
    if not shortcut.exists():
        url_shortcut = desktop / "Optótipos Profissional.url"
        url_shortcut.write_text(f"[InternetShortcut]\nURL=file:///{target.as_posix()}\n", encoding="utf-8")
        return url_shortcut
    return shortcut


def shutil_which(name: str) -> str | None:
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(folder) / name
        if candidate.exists():
            return str(candidate)
    return None
