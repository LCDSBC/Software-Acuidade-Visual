from __future__ import annotations

import json
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
OPERATIONAL_CHECKS = (
    "executaveis_abrem_sem_python",
    "pacote_portatil_copiado",
    "tela_unica_funciona",
    "duas_telas_funciona",
    "espelhamento_funciona",
    "controle_celular_funciona",
    "configuracoes_persistem",
)


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


@dataclass(frozen=True)
class FieldValidation:
    monitor_model: str
    resolution: str
    configured_distance_m: float
    ruler_100mm_measured_mm: float | None
    optotype_20_20_4m_measured_mm: float | None
    optotype_20_20_5m_measured_mm: float | None
    optotype_20_20_6m_measured_mm: float | None
    checks: dict[str, bool]
    notes: str = ""


@dataclass(frozen=True)
class ClinicalConfidence:
    score_percent: float
    level: str
    approved_for_clinic_trial: bool
    measurement_results: tuple[MeasurementResult, ...]
    passed_operational_checks: int
    total_operational_checks: int
    blockers: tuple[str, ...]

    def as_lines(self) -> list[str]:
        blockers = ", ".join(self.blockers) if self.blockers else "nenhum"
        return [
            f"Confianca clinica: {self.level}",
            f"Pontuacao: {self.score_percent:.1f}%",
            f"Aprovado para piloto em consultorio: {'SIM' if self.approved_for_clinic_trial else 'NAO'}",
            f"Checks operacionais: {self.passed_operational_checks}/{self.total_operational_checks}",
            f"Bloqueios: {blockers}",
        ]


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


def field_validation_from_dict(data: dict[str, object]) -> FieldValidation:
    checks = {name: bool(data.get("checks", {}).get(name, False)) if isinstance(data.get("checks"), dict) else False for name in OPERATIONAL_CHECKS}
    return FieldValidation(
        monitor_model=str(data.get("monitor_model", "")),
        resolution=str(data.get("resolution", "")),
        configured_distance_m=float(data.get("configured_distance_m", 4.0)),
        ruler_100mm_measured_mm=optional_float(data.get("ruler_100mm_measured_mm")),
        optotype_20_20_4m_measured_mm=optional_float(data.get("optotype_20_20_4m_measured_mm")),
        optotype_20_20_5m_measured_mm=optional_float(data.get("optotype_20_20_5m_measured_mm")),
        optotype_20_20_6m_measured_mm=optional_float(data.get("optotype_20_20_6m_measured_mm")),
        checks=checks,
        notes=str(data.get("notes", "")),
    )


def optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def load_field_validation(path: Path) -> FieldValidation:
    return field_validation_from_dict(json.loads(path.read_text(encoding="utf-8")))


def evaluate_clinical_confidence(field: FieldValidation | None, status: PortableStatus | None = None) -> ClinicalConfidence:
    if field is None:
        return ClinicalConfidence(
            score_percent=0.0,
            level="PENDENTE - sem medicao fisica",
            approved_for_clinic_trial=False,
            measurement_results=(),
            passed_operational_checks=0,
            total_operational_checks=len(OPERATIONAL_CHECKS),
            blockers=("medicao fisica nao informada",),
        )

    measurements: list[MeasurementResult] = []
    if field.ruler_100mm_measured_mm is not None:
        measurements.append(measurement_result("Regua virtual 100 mm", 100.0, field.ruler_100mm_measured_mm))
    expected_by_distance = {item.distance_m: item.expected_height_mm for item in expected_20_20_measurements()}
    measured_by_distance = {
        4.0: field.optotype_20_20_4m_measured_mm,
        5.0: field.optotype_20_20_5m_measured_mm,
        6.0: field.optotype_20_20_6m_measured_mm,
    }
    for distance, measured in measured_by_distance.items():
        if measured is not None:
            measurements.append(measurement_result(f"Optotipo 20/20 a {distance:g} m", expected_by_distance[distance], measured))

    measurement_score = 0.0
    if measurements:
        measurement_score = sum(max(0.0, 100.0 - min(result.error_percent, 100.0)) for result in measurements) / len(measurements)

    passed_checks = sum(1 for value in field.checks.values() if value)
    operational_score = passed_checks / len(OPERATIONAL_CHECKS) * 100
    package_score = 100.0
    blockers: list[str] = []

    if status is not None and not status.ready_for_windows_trial:
        package_score = 0.0
        blockers.append("executaveis ou configuracoes incompletos no pacote")

    if not measurements:
        blockers.append("nenhuma medicao fisica preenchida")
    if measurements and not all(result.passed for result in measurements):
        blockers.append("erro fisico acima do limite em uma ou mais medicoes")
    if not field.checks.get("executaveis_abrem_sem_python", False):
        blockers.append("executaveis ainda nao confirmados sem Python")
    if not field.checks.get("tela_unica_funciona", False):
        blockers.append("tela unica ainda nao confirmada")

    score = measurement_score * 0.55 + operational_score * 0.35 + package_score * 0.10
    critical_passed = bool(measurements) and all(result.passed for result in measurements) and field.checks.get("executaveis_abrem_sem_python", False) and field.checks.get("tela_unica_funciona", False)
    approved = score >= 90 and critical_passed and not blockers
    level = clinical_confidence_level(score, critical_passed, blockers)
    return ClinicalConfidence(
        score_percent=score,
        level=level,
        approved_for_clinic_trial=approved,
        measurement_results=tuple(measurements),
        passed_operational_checks=passed_checks,
        total_operational_checks=len(OPERATIONAL_CHECKS),
        blockers=tuple(blockers),
    )


def clinical_confidence_level(score: float, critical_passed: bool, blockers: list[str]) -> str:
    if blockers and not critical_passed:
        if score >= 75:
            return "MODERADA COM BLOQUEIOS"
        return "BAIXA"
    if score >= 90 and critical_passed:
        return "ALTA"
    if score >= 75:
        return "MODERADA"
    return "BAIXA"


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


def build_validation_report(config: RuntimeConfig | None = None, root: Path | None = None, field_validation: FieldValidation | None = None) -> str:
    config = config or load_config(root)
    calibration = calibration_from_config(config)
    status = portable_status(config.root)
    report = calibration_report(calibration)
    confidence = evaluate_clinical_confidence(field_validation, status)
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
        "## Confianca clinica",
        "",
        *confidence.as_lines(),
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
            "## Resultado das medicoes informadas",
            "",
        ]
    )
    if confidence.measurement_results:
        lines.extend(
            [
                "| Item | Esperado | Medido | Erro | Erro % | Aprovado |",
                "| --- | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for result in confidence.measurement_results:
            lines.append(
                f"| {result.label} | {result.expected_mm:.4f} mm | {result.measured_mm:.4f} mm | "
                f"{result.error_mm:+.4f} mm | {result.error_percent:.2f}% | {'SIM' if result.passed else 'NAO'} |"
            )
    else:
        lines.append("Nenhuma medicao fisica informada. Confianca clinica permanece pendente.")

    lines.extend(
        [
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


def write_validation_report(destination: Path, config: RuntimeConfig | None = None, root: Path | None = None, field_validation: FieldValidation | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_validation_report(config=config, root=root, field_validation=field_validation), encoding="utf-8")
    return destination
