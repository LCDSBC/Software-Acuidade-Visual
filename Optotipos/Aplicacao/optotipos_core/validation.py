from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .calibration import (
    DisplayCalibration,
    calibration_from_config,
    calibration_report,
    logmar_from_denominator,
    snellen_letter_height_mm,
)
from .config import RuntimeConfig, load_config
from .paths import ensure_portable_tree


DEFAULT_VALIDATION_DISTANCES_M = (4.0, 5.0, 6.0)
DEFAULT_ERROR_LIMIT_PERCENT = 2.0


@dataclass(frozen=True)
class OptotypeMeasurement:
    distance_m: float
    denominator_ft: float
    expected_height_mm: float
    expected_stroke_mm: float
    expected_logmar: float


@dataclass(frozen=True)
class MeasurementResult:
    label: str
    expected_mm: float
    measured_mm: float
    error_mm: float
    error_percent: float
    passed: bool


@dataclass(frozen=True)
class PortableStatus:
    root: Path
    optotipos_exe_exists: bool
    configurador_exe_exists: bool
    config_files_ok: bool
    profile_count: int

    @property
    def ready_for_windows_trial(self) -> bool:
        return self.optotipos_exe_exists and self.configurador_exe_exists and self.config_files_ok


def expected_20_20_measurements(distances_m: tuple[float, ...] = DEFAULT_VALIDATION_DISTANCES_M) -> list[OptotypeMeasurement]:
    return [
        OptotypeMeasurement(
            distance_m=distance,
            denominator_ft=20,
            expected_height_mm=snellen_letter_height_mm(distance, 20),
            expected_stroke_mm=snellen_letter_height_mm(distance, 20) / 5,
            expected_logmar=logmar_from_denominator(20),
        )
        for distance in distances_m
    ]


def measurement_result(label: str, expected_mm: float, measured_mm: float, limit_percent: float = DEFAULT_ERROR_LIMIT_PERCENT) -> MeasurementResult:
    error_mm = measured_mm - expected_mm
    error_percent = abs(error_mm) / expected_mm * 100 if expected_mm else 100.0
    return MeasurementResult(
        label=label,
        expected_mm=expected_mm,
        measured_mm=measured_mm,
        error_mm=error_mm,
        error_percent=error_percent,
        passed=error_percent <= limit_percent,
    )


def portable_status(root: Path | None = None) -> PortableStatus:
    root = ensure_portable_tree(root)
    required_config_files = (
        "Tela.txt",
        "Distancia.txt",
        "Escala.txt",
        "Inversao.txt",
        "Monitores.txt",
        "Exibicao.txt",
        "Atalhos.txt",
    )
    return PortableStatus(
        root=root,
        optotipos_exe_exists=(root / "Optotipos.exe").exists(),
        configurador_exe_exists=(root / "Configurador.exe").exists(),
        config_files_ok=all((root / "Configuracoes" / file_name).exists() for file_name in required_config_files),
        profile_count=len(list((root / "Perfis").glob("*.ini"))),
    )


def build_validation_report(config: RuntimeConfig | None = None, root: Path | None = None) -> str:
    config = config or load_config(root)
    calibration = calibration_from_config(config)
    status = portable_status(config.root)
    report = calibration_report(calibration)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Relatorio de Validacao Clinica - Fase 4",
        "",
        f"Gerado em: {now}",
        f"Pasta portatil: {status.root}",
        "",
        "## Status do pacote portatil",
        "",
        f"Optotipos.exe encontrado: {'SIM' if status.optotipos_exe_exists else 'NAO'}",
        f"Configurador.exe encontrado: {'SIM' if status.configurador_exe_exists else 'NAO'}",
        f"Configuracoes completas: {'SIM' if status.config_files_ok else 'NAO'}",
        f"Perfis encontrados: {status.profile_count}",
        f"Pronto para teste Windows: {'SIM' if status.ready_for_windows_trial else 'NAO'}",
        "",
        "## Calibracao carregada",
        "",
        *report.as_lines(),
        "",
        "## Tamanho esperado do optotipo 20/20",
        "",
        "| Distancia | Altura esperada | Traco esperado | LogMAR |",
        "| --- | ---: | ---: | ---: |",
    ]
    for measurement in expected_20_20_measurements():
        lines.append(
            f"| {measurement.distance_m:g} m | {measurement.expected_height_mm:.4f} mm | "
            f"{measurement.expected_stroke_mm:.4f} mm | {measurement.expected_logmar:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Registro de medicao fisica",
            "",
            "Preencher durante o teste em consultorio:",
            "",
            "| Item | Esperado | Medido | Erro | Aprovado |",
            "| --- | ---: | ---: | ---: | --- |",
            "| Regua virtual 100 mm | 100.00 mm | ____ mm | ____ | ____ |",
            "| Optotipo 20/20 a 4 m | 5.8178 mm | ____ mm | ____ | ____ |",
            "| Optotipo 20/20 a 5 m | 7.2722 mm | ____ mm | ____ | ____ |",
            "| Optotipo 20/20 a 6 m | 8.7266 mm | ____ mm | ____ | ____ |",
            "",
            "Criterio sugerido para MVP clinico: erro fisico <= 2% apos calibracao.",
            "",
            "## Checklist operacional",
            "",
            "- [ ] Executar `Optotipos.exe` sem Python instalado.",
            "- [ ] Executar `Configurador.exe` sem Python instalado.",
            "- [ ] Testar em pendrive ou pasta copiada.",
            "- [ ] Calibrar regua virtual com regua fisica.",
            "- [ ] Medir 20/20 na distancia configurada.",
            "- [ ] Testar TelaUnica.",
            "- [ ] Testar DuasTelas.",
            "- [ ] Testar Espelhamento.",
            "- [ ] Testar controle por celular na mesma rede.",
            "- [ ] Registrar modelo da TV/monitor e resolucao usada.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_validation_report(destination: Path, config: RuntimeConfig | None = None, root: Path | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_validation_report(config=config, root=root), encoding="utf-8")
    return destination
