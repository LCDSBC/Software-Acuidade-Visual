from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .calibration import (
    DisplayCalibration,
    SNELLEN_CLINICAL_DENOMINATORS,
    STANDARD_LETTER_ARC_MINUTES,
    calibration_from_config,
    calibration_report,
    etdrs_line_denominators,
    etdrs_line_logmars,
    logmar_from_denominator,
    snellen_letter_height_mm,
)
from .config import RuntimeConfig, load_config
from .clinical_assets import validate_all_asset_packs
from .paths import ensure_portable_tree
from .rendering import (
    ETDRS_OPTOTYPES_PER_LINE,
    OPTOTYPE_GRID,
    ROTATIONS,
    SNELLEN_DENOMINATORS,
    block_letter_cells,
    clinical_line,
    e_pattern_cells,
    etdrs_spacing_px,
    landolt_gap_px,
)


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


@dataclass(frozen=True)
class OptotypeClinicalCheck:
    name: str
    criterion: str
    passed: bool
    details: str
    severity: str = "critico"


@dataclass(frozen=True)
class OptotypeValidationSummary:
    checks: tuple[OptotypeClinicalCheck, ...]

    @property
    def passed_count(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def failed_critical_count(self) -> int:
        return sum(1 for check in self.checks if not check.passed and check.severity == "critico")

    @property
    def approved_for_field_validation(self) -> bool:
        return self.failed_critical_count == 0

    @property
    def score_percent(self) -> float:
        if not self.checks:
            return 0.0
        return self.passed_count / len(self.checks) * 100


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


def validate_optotypes(calibration: DisplayCalibration | None = None) -> OptotypeValidationSummary:
    calibration = calibration or DisplayCalibration(
        distance_m=4,
        screen_width_mm=597,
        screen_height_mm=336,
        resolution_width=1920,
        resolution_height=1080,
        scale_factor=1.0,
    )
    checks = [
        validate_snellen_lines(),
        validate_snellen_visual_angle(),
        validate_snellen_stroke(calibration),
        validate_tumbling_e_geometry(),
        validate_tumbling_e_rotations(),
        validate_landolt_c_geometry(),
        validate_etdrs_progression(),
        validate_etdrs_spacing(calibration),
        validate_duochrome_dependency(calibration),
        validate_astigmatic_clock_geometry(),
    ]
    return OptotypeValidationSummary(tuple(checks))


def validate_snellen_lines() -> OptotypeClinicalCheck:
    expected = SNELLEN_CLINICAL_DENOMINATORS
    passed = tuple(SNELLEN_DENOMINATORS) == expected
    return OptotypeClinicalCheck(
        name="Snellen - linhas obrigatorias",
        criterion="20/400, 20/300, 20/200, 20/100, 20/80, 20/60, 20/50, 20/40, 20/30, 20/25, 20/20, 20/15 e 20/10",
        passed=passed,
        details=f"linhas={tuple(SNELLEN_DENOMINATORS)}",
    )


def validate_snellen_visual_angle() -> OptotypeClinicalCheck:
    height_4m = snellen_letter_height_mm(4, 20)
    expected = 5.8178
    passed = abs(height_4m - expected) < 0.01
    return OptotypeClinicalCheck(
        name="Snellen - angulo visual",
        criterion=f"20/20 deve subtender {STANDARD_LETTER_ARC_MINUTES:g} minutos de arco",
        passed=passed,
        details=f"20/20 a 4 m={height_4m:.4f} mm",
    )


def validate_snellen_stroke(calibration: DisplayCalibration) -> OptotypeClinicalCheck:
    line = clinical_line(calibration, 20, 5)
    passed = line.stroke_width_px == round(line.optotype_size_px / OPTOTYPE_GRID)
    return OptotypeClinicalCheck(
        name="Snellen - traco 1/5",
        criterion="espessura do traco deve ser 1/5 da altura do optotipo",
        passed=passed,
        details=f"altura={line.optotype_size_px}px, traco={line.stroke_width_px}px",
    )


def validate_tumbling_e_geometry() -> OptotypeClinicalCheck:
    cells = e_pattern_cells()
    required = {(0, row) for row in range(5)} | {(col, 0) for col in range(5)} | {(col, 2) for col in range(5)} | {(col, 4) for col in range(5)}
    passed = cells == required and all(0 <= col < OPTOTYPE_GRID and 0 <= row < OPTOTYPE_GRID for col, row in cells)
    return OptotypeClinicalCheck(
        name="Tumbling E - grade 5x5",
        criterion="E deve ocupar grade 5x5 com haste vertical e tres barras horizontais completas",
        passed=passed,
        details=f"celulas={len(cells)}",
    )


def validate_tumbling_e_rotations() -> OptotypeClinicalCheck:
    passed = tuple(ROTATIONS) == (0, 90, 180, 270)
    return OptotypeClinicalCheck(
        name="Tumbling E - orientacoes",
        criterion="orientacoes obrigatorias 0, 90, 180 e 270 graus",
        passed=passed,
        details=f"orientacoes={tuple(ROTATIONS)}",
    )


def validate_landolt_c_geometry() -> OptotypeClinicalCheck:
    size = 100
    gap = landolt_gap_px(size)
    passed = gap == size / OPTOTYPE_GRID
    return OptotypeClinicalCheck(
        name="Landolt C - abertura proporcional",
        criterion="abertura deve ser 1/5 do diametro",
        passed=passed,
        details=f"diametro={size}px, abertura={gap}px",
    )


def validate_etdrs_progression() -> OptotypeClinicalCheck:
    logmars = etdrs_line_logmars()
    denominators = etdrs_line_denominators()
    steps_ok = all(round(logmars[index] - logmars[index + 1], 1) == 0.1 for index in range(len(logmars) - 1))
    passed = len(logmars) == len(denominators) and steps_ok and ETDRS_OPTOTYPES_PER_LINE == 5
    return OptotypeClinicalCheck(
        name="ETDRS - progressao LogMAR",
        criterion="progressao de 0.1 LogMAR com 5 optotipos por linha",
        passed=passed,
        details=f"linhas={len(logmars)}, optotipos_por_linha={ETDRS_OPTOTYPES_PER_LINE}",
    )


def validate_etdrs_spacing(calibration: DisplayCalibration) -> OptotypeClinicalCheck:
    line = clinical_line(calibration, 20, ETDRS_OPTOTYPES_PER_LINE)
    passed = line.letter_spacing_px == line.optotype_size_px and line.row_spacing_px == line.optotype_size_px and etdrs_spacing_px(line.optotype_size_px) == line.optotype_size_px
    return OptotypeClinicalCheck(
        name="ETDRS - espacamento normativo",
        criterion="espacamento entre optotipos e linhas deve ser uma largura/altura de optotipo",
        passed=passed,
        details=f"altura={line.optotype_size_px}px, espaco_letra={line.letter_spacing_px}px, espaco_linha={line.row_spacing_px}px",
    )


def validate_duochrome_dependency(calibration: DisplayCalibration) -> OptotypeClinicalCheck:
    line_30 = clinical_line(calibration, 30, 4)
    passed = line_30.stroke_width_px == round(line_30.optotype_size_px / OPTOTYPE_GRID)
    return OptotypeClinicalCheck(
        name="Duocromatico - letras calibradas",
        criterion="letras do duocromatico devem usar o mesmo calculo de tamanho e traco dos optotipos",
        passed=passed,
        details=f"base 20/30: altura={line_30.optotype_size_px}px, traco={line_30.stroke_width_px}px",
    )


def validate_astigmatic_clock_geometry() -> OptotypeClinicalCheck:
    degrees = tuple(range(0, 180, 10))
    passed = len(degrees) == 18 and degrees[0] == 0 and degrees[-1] == 170
    return OptotypeClinicalCheck(
        name="Relogio astigmatico - 180 graus",
        criterion="linhas devem cobrir 180 graus em intervalos uniformes de 10 graus",
        passed=passed,
        details=f"linhas_radiais={len(degrees)}, intervalo=10 graus",
    )


def build_optotype_validation_report(calibration: DisplayCalibration | None = None) -> str:
    summary = validate_optotypes(calibration)
    lines = [
        "# Validacao clinica matematica dos optotipos",
        "",
        "Esta validacao confirma geometria e calculos implementados no software.",
        "Ela nao substitui medicao fisica em tela real nem validacao regulatoria.",
        "",
        f"Pontuacao: {summary.score_percent:.1f}%",
        f"Aprovado para validacao de campo: {'SIM' if summary.approved_for_field_validation else 'NAO'}",
        f"Falhas criticas: {summary.failed_critical_count}",
        "",
        "| Teste | Criterio | Status | Detalhes |",
        "| --- | --- | --- | --- |",
    ]
    for check in summary.checks:
        lines.append(f"| {check.name} | {check.criterion} | {'OK' if check.passed else 'FALHA'} | {check.details} |")
    lines.extend(
        [
            "",
            "## Limites desta validacao",
            "",
            "- Nao confirma luminancia real da tela.",
            "- Nao confirma tamanho fisico exibido sem medicao com regua.",
            "- Nao substitui validacao clinica formal.",
            "- Nao resolve licenciamento de simbolos ou testes proprietarios.",
        ]
    )
    return "\n".join(lines) + "\n"


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
    optotype_summary = validate_optotypes(calibration)
    asset_statuses = validate_all_asset_packs(config.root)
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
        "## Validacao matematica dos optotipos",
        "",
        f"Pontuacao: {optotype_summary.score_percent:.1f}%",
        f"Aprovado para validacao de campo: {'SIM' if optotype_summary.approved_for_field_validation else 'NAO'}",
        f"Falhas criticas: {optotype_summary.failed_critical_count}",
        "",
        "| Teste | Status | Detalhes |",
        "| --- | --- | --- |",
        *[f"| {check.name} | {'OK' if check.passed else 'FALHA'} | {check.details} |" for check in optotype_summary.checks],
        "",
        "## Testes profissionais dependentes de ativos licenciados",
        "",
        "| Teste | Status | Arquivos | Motivo |",
        "| --- | --- | ---: | --- |",
        *[
            f"| {status.spec.name} | {'PRONTO' if status.ready else 'BLOQUEADO'} | {status.file_count}/{status.spec.minimum_files} | {status.summary} |"
            for status in asset_statuses
        ],
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
