from __future__ import annotations

import configparser
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .paths import config_path, ensure_portable_tree, profile_path


CONFIG_FILES = (
    "Tela.txt",
    "Distancia.txt",
    "Escala.txt",
    "Inversao.txt",
    "Monitores.txt",
    "Exibicao.txt",
    "Atalhos.txt",
)


DEFAULT_CONFIG: dict[str, dict[str, str]] = {
    "Tela.txt": {
        "Polegadas": "27",
        "LarguraTelaMM": "597",
        "AlturaTelaMM": "336",
        "ResolucaoLargura": "1920",
        "ResolucaoAltura": "1080",
    },
    "Distancia.txt": {
        "Distancia": "4",
        "Unidade": "m",
    },
    "Escala.txt": {
        "FatorEscala": "1.0000",
        "Polegadas": "27",
        "LarguraTelaMM": "597",
        "AlturaTelaMM": "336",
    },
    "Inversao.txt": {
        "Horizontal": "OFF",
        "Vertical": "OFF",
        "Rotacao": "0",
    },
    "Monitores.txt": {
        "Modo": "TelaUnica",
        "MonitorExaminador": "0",
        "MonitorTeste": "0",
    },
    "Exibicao.txt": {
        "TelaCheia": "ON",
        "BarraFerramentas": "ON",
        "Fundo": "branco",
        "Brilho": "100",
        "Luminancia": "100",
        "UltimoPerfil": "Consultorio_4m.ini",
        "Filtro": "Nenhum",
    },
    "Atalhos.txt": {
        "ConfiguracoesAvancadas": "CTRL+ALT+C",
        "ProximoTeste": "Right",
        "TesteAnterior": "Left",
        "Aumentar": "plus",
        "Diminuir": "minus",
        "Aleatorio": "R",
    },
}


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    values: dict[str, dict[str, str]]

    def section(self, file_name: str) -> dict[str, str]:
        return dict(self.values.get(file_name, {}))

    def get(self, file_name: str, key: str, default: str = "") -> str:
        return self.values.get(file_name, {}).get(key, default)

    def get_float(self, file_name: str, key: str, default: float) -> float:
        try:
            return float(self.get(file_name, key, str(default)).replace(",", "."))
        except ValueError:
            return default

    def get_int(self, file_name: str, key: str, default: int) -> int:
        try:
            return int(float(self.get(file_name, key, str(default)).replace(",", ".")))
        except ValueError:
            return default

    def get_bool(self, file_name: str, key: str, default: bool = False) -> bool:
        raw = self.get(file_name, key, "ON" if default else "OFF").strip().upper()
        return raw in {"ON", "TRUE", "1", "YES", "SIM"}


def parse_key_value(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def format_key_value(values: dict[str, str]) -> str:
    return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"


def ensure_default_config(root: Path | None = None) -> Path:
    root = ensure_portable_tree(root)
    for file_name in CONFIG_FILES:
        path = config_path(file_name, root)
        if not path.exists():
            path.write_text(format_key_value(DEFAULT_CONFIG[file_name]), encoding="utf-8")
    return root


def load_config(root: Path | None = None) -> RuntimeConfig:
    root = ensure_default_config(root)
    values: dict[str, dict[str, str]] = {}
    for file_name in CONFIG_FILES:
        path = config_path(file_name, root)
        current = dict(DEFAULT_CONFIG[file_name])
        if path.exists():
            current.update(parse_key_value(path.read_text(encoding="utf-8")))
        values[file_name] = current
    return RuntimeConfig(root=root, values=values)


def save_config_file(file_name: str, values: dict[str, str], root: Path | None = None) -> None:
    if file_name not in DEFAULT_CONFIG:
        raise ValueError(f"Arquivo de configuracao desconhecido: {file_name}")
    root = ensure_default_config(root)
    merged = dict(DEFAULT_CONFIG[file_name])
    merged.update({key: str(value) for key, value in values.items()})
    config_path(file_name, root).write_text(format_key_value(merged), encoding="utf-8")


def save_profile(name: str, root: Path | None = None) -> Path:
    runtime = load_config(root)
    parser = configparser.ConfigParser()
    parser.optionxform = str
    for file_name, values in runtime.values.items():
        parser[file_name] = values
    path = profile_path(name, runtime.root)
    with path.open("w", encoding="utf-8") as handle:
        parser.write(handle, space_around_delimiters=False)
    save_config_file("Exibicao.txt", {"UltimoPerfil": path.name}, runtime.root)
    return path


def load_profile(name: str, root: Path | None = None) -> Path:
    root = ensure_default_config(root)
    path = profile_path(name, root)
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(path, encoding="utf-8")
    if not parser.sections():
        raise FileNotFoundError(path)
    for file_name in CONFIG_FILES:
        if parser.has_section(file_name):
            save_config_file(file_name, dict(parser[file_name]), root)
    save_config_file("Exibicao.txt", {"UltimoPerfil": path.name}, root)
    return path


def list_profiles(root: Path | None = None) -> list[Path]:
    root = ensure_default_config(root)
    return sorted((root / "Perfis").glob("*.ini"))


def export_profile(source_name: str, destination: Path, root: Path | None = None) -> Path:
    source = profile_path(source_name, ensure_default_config(root))
    if not source.exists():
        raise FileNotFoundError(source)
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def import_profile(source: Path, root: Path | None = None) -> Path:
    root = ensure_default_config(root)
    if not source.exists():
        raise FileNotFoundError(source)
    destination = root / "Perfis" / source.name
    shutil.copy2(source, destination)
    return destination


def export_backup(destination: Path | None = None, root: Path | None = None) -> Path:
    root = ensure_default_config(root)
    destination = destination or (root / "Backup" / "BackupCalibracao.opt")
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name in CONFIG_FILES:
            path = config_path(file_name, root)
            archive.write(path, f"Configuracoes/{file_name}")
        for profile in list_profiles(root):
            archive.write(profile, f"Perfis/{profile.name}")
    return destination


def import_backup(source: Path, root: Path | None = None) -> Path:
    root = ensure_default_config(root)
    if not source.exists():
        raise FileNotFoundError(source)
    with zipfile.ZipFile(source, "r") as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_path = Path(member.filename)
            if member_path.parts[0] not in {"Configuracoes", "Perfis"}:
                continue
            target = root / member_path
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    return root
