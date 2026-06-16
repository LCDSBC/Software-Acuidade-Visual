from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .paths import ensure_portable_tree


ASSET_ROOT = "Assets"


@dataclass(frozen=True)
class ClinicalAssetSpec:
    test_key: str
    name: str
    asset_type: str
    minimum_files: int
    required_fields: tuple[str, ...] = ("license", "source", "version", "files")
    instructions: str = ""


@dataclass(frozen=True)
class ClinicalAssetStatus:
    spec: ClinicalAssetSpec
    root: Path
    manifest_path: Path
    manifest_exists: bool
    licensed: bool
    file_count: int
    missing_files: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.manifest_exists and self.licensed and self.file_count >= self.spec.minimum_files and not self.missing_files and not self.errors

    @property
    def summary(self) -> str:
        if self.ready:
            return f"{self.spec.name}: ativos licenciados prontos ({self.file_count} arquivo(s))."
        details = "; ".join(self.errors) if self.errors else "ativos licenciados ausentes ou incompletos"
        return f"{self.spec.name}: {details}."


LICENSED_ASSET_SPECS: dict[str, ClinicalAssetSpec] = {
    "ishihara": ClinicalAssetSpec(
        test_key="ishihara",
        name="Ishihara",
        asset_type="color_plates",
        minimum_files=24,
        instructions="Instale placas Ishihara licenciadas em Testes/Assets/ishihara/.",
    ),
    "hrr": ClinicalAssetSpec(
        test_key="hrr",
        name="HRR",
        asset_type="color_plates",
        minimum_files=14,
        instructions="Instale placas HRR licenciadas em Testes/Assets/hrr/.",
    ),
    "wirt_circles": ClinicalAssetSpec(
        test_key="wirt_circles",
        name="Circulos de Wirt",
        asset_type="stereo_plate",
        minimum_files=1,
        instructions="Instale prancha Wirt/licenciada em Testes/Assets/wirt_circles/.",
    ),
    "randot": ClinicalAssetSpec(
        test_key="randot",
        name="Randot",
        asset_type="stereo_plate",
        minimum_files=1,
        instructions="Instale ativos Randot licenciados em Testes/Assets/randot/.",
    ),
    "fly_test": ClinicalAssetSpec(
        test_key="fly_test",
        name="Fly Test",
        asset_type="stereo_plate",
        minimum_files=1,
        instructions="Instale prancha Fly Test licenciada em Testes/Assets/fly_test/.",
    ),
    "stereo_shapes": ClinicalAssetSpec(
        test_key="stereo_shapes",
        name="Stereo Shapes",
        asset_type="stereo_plate",
        minimum_files=1,
        instructions="Instale ativos de estereopsia licenciados em Testes/Assets/stereo_shapes/.",
    ),
    "vectograms": ClinicalAssetSpec(
        test_key="vectograms",
        name="Vetogramas",
        asset_type="binocular_vectogram",
        minimum_files=1,
        instructions="Instale vetogramas licenciados em Testes/Assets/vectograms/.",
    ),
    "polarized_filter": ClinicalAssetSpec(
        test_key="polarized_filter",
        name="Optotipos polarizados",
        asset_type="polarized_optotypes",
        minimum_files=1,
        instructions="Instale optotipos polarizados licenciados e valide o hardware polarizador.",
    ),
    "anaglyph_filter": ClinicalAssetSpec(
        test_key="anaglyph_filter",
        name="Optotipos anaglifos",
        asset_type="anaglyph_optotypes",
        minimum_files=1,
        instructions="Instale optotipos anaglifos licenciados e valide filtros vermelho/verde ou vermelho/azul.",
    ),
}


def asset_directory(test_key: str, root: Path | None = None) -> Path:
    return ensure_portable_tree(root) / "Testes" / ASSET_ROOT / test_key


def asset_manifest_path(test_key: str, root: Path | None = None) -> Path:
    return asset_directory(test_key, root) / "manifest.json"


def load_asset_manifest(test_key: str, root: Path | None = None) -> dict[str, object]:
    path = asset_manifest_path(test_key, root)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_asset_pack(test_key: str, root: Path | None = None) -> ClinicalAssetStatus:
    spec = LICENSED_ASSET_SPECS[test_key]
    directory = asset_directory(test_key, root)
    manifest_path = directory / "manifest.json"
    errors: list[str] = []
    missing_files: list[str] = []
    licensed = False
    file_count = 0

    if not manifest_path.exists():
        return ClinicalAssetStatus(spec, directory, manifest_path, False, False, 0, (), ("manifest.json ausente",))

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ClinicalAssetStatus(spec, directory, manifest_path, True, False, 0, (), (f"manifest.json invalido: {exc}",))

    for field in spec.required_fields:
        if field not in manifest:
            errors.append(f"campo obrigatorio ausente: {field}")

    license_info = manifest.get("license", {})
    if isinstance(license_info, dict):
        licensed = bool(license_info.get("licensed"))
        if not licensed:
            errors.append("licenca nao confirmada no manifesto")
    else:
        errors.append("campo license deve ser objeto")

    files = manifest.get("files", [])
    if not isinstance(files, list):
        errors.append("campo files deve ser lista")
        files = []
    file_count = len(files)
    if file_count < spec.minimum_files:
        errors.append(f"arquivos insuficientes: {file_count}/{spec.minimum_files}")

    for item in files:
        file_name = item.get("path") if isinstance(item, dict) else item
        if not isinstance(file_name, str) or not file_name:
            errors.append("entrada de arquivo invalida no manifesto")
            continue
        if not (directory / file_name).exists():
            missing_files.append(file_name)

    return ClinicalAssetStatus(spec, directory, manifest_path, True, licensed, file_count, tuple(missing_files), tuple(errors))


def validate_all_asset_packs(root: Path | None = None) -> list[ClinicalAssetStatus]:
    return [validate_asset_pack(test_key, root) for test_key in LICENSED_ASSET_SPECS]


def asset_ready(test_key: str, root: Path | None = None) -> bool:
    return validate_asset_pack(test_key, root).ready
