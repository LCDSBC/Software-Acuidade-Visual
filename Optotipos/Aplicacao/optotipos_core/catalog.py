from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisualTest:
    key: str
    name: str
    category: str
    renderer: str
    symbols: tuple[str, ...] = ()
    description: str = ""


SNELLEN_LETTERS = ("C", "D", "H", "K", "N", "O", "R", "S", "V", "Z")
SNELLEN_NUMBERS = ("2", "3", "4", "5", "6", "7", "8", "9")
HOTV = ("H", "O", "T", "V")
SHERIDAN = ("H", "O", "T", "V", "X", "U")
BAILEY_LOVIE = ("D", "E", "F", "H", "N", "P", "R", "U", "V", "Z")
ETDRS = ("S", "K", "D", "H", "O", "N", "V", "C", "R", "Z")
LANDOLT = ("C",)
TUMBLING_E = ("E",)
LEA = ("circle", "square", "house", "apple")
ALLEN = ("cake", "hand", "horse", "phone")


TESTS: tuple[VisualTest, ...] = (
    VisualTest("snellen_letters", "Snellen Letras", "Acuidade visual", "chart", SNELLEN_LETTERS),
    VisualTest("snellen_numbers", "Snellen Numeros", "Acuidade visual", "chart", SNELLEN_NUMBERS),
    VisualTest("tumbling_e", "Tumbling E", "Acuidade visual", "directional", TUMBLING_E),
    VisualTest("directional_e", "E Direcional", "Acuidade visual", "directional", TUMBLING_E),
    VisualTest("landolt_c", "Landolt C", "Acuidade visual", "landolt", LANDOLT),
    VisualTest("hotv", "HOTV", "Acuidade visual", "chart", HOTV),
    VisualTest("lea_symbols", "LEA Symbols", "Acuidade visual", "shapes", LEA),
    VisualTest("allen_figures", "Allen Figures", "Acuidade visual", "shapes", ALLEN),
    VisualTest("sheridan_gardiner", "Sheridan Gardiner", "Acuidade visual", "chart", SHERIDAN),
    VisualTest("bailey_lovie", "Bailey-Lovie", "Acuidade visual", "chart", BAILEY_LOVIE),
    VisualTest("logmar_etdrs", "LogMAR ETDRS", "Acuidade visual", "etdrs", ETDRS),
    VisualTest("duochrome", "Duocromatico", "Refracao", "duochrome"),
    VisualTest("astigmatic_clock", "Relogio Astigmatico", "Refracao", "clock"),
    VisualTest("astigmatic_fan", "Ventilador Astigmatico", "Refracao", "fan"),
    VisualTest("cross_cylinder", "Cilindro Cruzado", "Refracao", "cross_cylinder"),
    VisualTest("bichromatic", "Bicromatico", "Refracao", "duochrome"),
    VisualTest("red_green", "Vermelho-Verde", "Refracao", "duochrome"),
    VisualTest("fogging", "Nevoa Refrativa", "Refracao", "fogging"),
    VisualTest("binocular_balance", "Equilibrio Binocular", "Refracao", "balance"),
    VisualTest("worth_4", "Worth 4 Pontos", "Binoculares", "worth"),
    VisualTest("vectograms", "Vetogramas", "Binoculares", "vectogram"),
    VisualTest("suppression", "Supressao", "Binoculares", "suppression"),
    VisualTest("fusion", "Fusao", "Binoculares", "fusion"),
    VisualTest("vergence", "Vergencia", "Binoculares", "vergence"),
    VisualTest("fixation_disparity", "Disparidade de Fixacao", "Binoculares", "fixation"),
    VisualTest("wirt_circles", "Circulos de Wirt", "Estereopsia", "stereo_circles"),
    VisualTest("randot", "Randot", "Estereopsia", "randot"),
    VisualTest("fly_test", "Fly Test", "Estereopsia", "fly"),
    VisualTest("stereo_shapes", "Stereo Shapes", "Estereopsia", "stereo_shapes"),
    VisualTest("h_test", "H Test", "Motilidade ocular", "motility_h"),
    VisualTest("versions", "Versoes", "Motilidade ocular", "motility_points"),
    VisualTest("ductions", "Duccoes", "Motilidade ocular", "motility_points"),
    VisualTest("saccades", "Sacadicos", "Motilidade ocular", "saccades"),
    VisualTest("pursuits", "Pursuits", "Motilidade ocular", "pursuits"),
    VisualTest("pelli_robson", "Pelli-Robson", "Contraste", "contrast_letters"),
    VisualTest("contrast_levels", "Contraste por niveis", "Contraste", "contrast_levels"),
    VisualTest("sine_contrast", "Contraste senoidal", "Contraste", "sine_contrast"),
    VisualTest("ishihara", "Ishihara", "Cores", "ishihara"),
    VisualTest("hrr", "HRR", "Cores", "hrr"),
    VisualTest("farnsworth_d15", "Farnsworth D15", "Cores", "hue_tiles"),
    VisualTest("farnsworth_100", "Farnsworth 100 Hue", "Cores", "hue_tiles_large"),
    VisualTest("red_filter", "Filtro Vermelho", "Filtros", "filter_red"),
    VisualTest("green_filter", "Filtro Verde", "Filtros", "filter_green"),
    VisualTest("blue_filter", "Filtro Azul", "Filtros", "filter_blue"),
    VisualTest("polarized_filter", "Filtro Polarizado", "Filtros", "filter_polarized"),
    VisualTest("anaglyph_filter", "Filtro Anaglifo", "Filtros", "filter_anaglyph"),
)


def categories() -> list[str]:
    seen: list[str] = []
    for test in TESTS:
        if test.category not in seen:
            seen.append(test.category)
    return seen


def tests_by_category(category: str) -> list[VisualTest]:
    return [test for test in TESTS if test.category == category]


def test_by_key(key: str) -> VisualTest:
    for test in TESTS:
        if test.key == key:
            return test
    return TESTS[0]
