export type OptotypeFamily =
  | 'sloan'
  | 'numbers'
  | 'tumbling-e'
  | 'landolt-c'
  | 'hotv'
  | 'lea'
  | 'allen'
  | 'gardiner'
  | 'bailey-lovie'
  | 'etdrs'

export interface AcuityLevel {
  denominator: number
  snellen20: string
  snellen6: string
  decimal: number
  logMAR: number
  etdrsLetters: number
}

export interface OptotypeMetric {
  heightMM: number
  fontSizePx: number
  strokeWidthPx: number
}

const FIVE_ARCMIN_RAD = (5 / 60) * (Math.PI / 180)
const CAP_HEIGHT_RATIO = 0.72

export const SLOAN_LETTERS = ['C', 'D', 'H', 'K', 'N', 'O', 'R', 'S', 'V', 'Z'] as const
export const HOTV_LETTERS = ['H', 'O', 'T', 'V'] as const
export const NUMBERS = ['2', '3', '4', '5', '6', '7', '8', '9'] as const
export const LEA_SYMBOLS = ['●', '■', '⬟', '⌂'] as const

export const SNELLEN_DENOMINATORS = [200, 160, 125, 100, 80, 63, 50, 40, 32, 25, 20, 16, 12.5, 10]

export const ACUITY_LEVELS: AcuityLevel[] = SNELLEN_DENOMINATORS.map((denominator, index) => ({
  denominator,
  snellen20: `20/${formatDenominator(denominator)}`,
  snellen6: `6/${formatDenominator((denominator * 6) / 20)}`,
  decimal: round(20 / denominator, 2),
  logMAR: round(Math.log10(denominator / 20), 2),
  etdrsLetters: Math.max(0, 85 - index * 5),
}))

export function formatDenominator(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1).replace('.', ',')
}

function round(value: number, decimals: number): number {
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}

export function optotypeHeightMM(denominator: number, distanceMM: number): number {
  const angle = FIVE_ARCMIN_RAD * (denominator / 20)
  return 2 * distanceMM * Math.tan(angle / 2)
}

export function optotypeMetric(denominator: number, distanceMM: number, pixelsPerMM: number): OptotypeMetric {
  const heightMM = optotypeHeightMM(denominator, distanceMM)
  const fontSizePx = (heightMM * pixelsPerMM) / CAP_HEIGHT_RATIO
  return {
    heightMM,
    fontSizePx,
    strokeWidthPx: Math.max(1, (heightMM * pixelsPerMM) / 5),
  }
}

export function symbolsForFamily(family: OptotypeFamily): readonly string[] {
  switch (family) {
    case 'numbers':
      return NUMBERS
    case 'hotv':
      return HOTV_LETTERS
    case 'lea':
      return LEA_SYMBOLS
    case 'tumbling-e':
      return ['E']
    case 'landolt-c':
      return ['C']
    case 'allen':
      return ['☎', '★', '☂', '◆']
    case 'gardiner':
      return ['A', 'H', 'O', 'T', 'U', 'V', 'X']
    case 'bailey-lovie':
    case 'etdrs':
    case 'sloan':
    default:
      return SLOAN_LETTERS
  }
}

export function generateOptotypes(family: OptotypeFamily, count: number, seed = Date.now()): string[] {
  const symbols = symbolsForFamily(family)
  let state = seed % 2147483647
  const result: string[] = []
  for (let index = 0; index < count; index += 1) {
    state = (state * 48271) % 2147483647
    let symbol = symbols[state % symbols.length]
    if (symbols.length > 1 && symbol === result.at(-1)) {
      symbol = symbols[(symbols.indexOf(symbol) + 1) % symbols.length]
    }
    result.push(symbol)
  }
  return result
}

export type TestCategory =
  | 'Tabelas de acuidade visual'
  | 'Testes de refração'
  | 'Testes binoculares'
  | 'Estereopsia'
  | 'Motilidade ocular'
  | 'Testes de contraste'
  | 'Testes de cores'
  | 'Filtros'

export type TestTemplate =
  | 'acuity'
  | 'duochrome'
  | 'astigmatic'
  | 'cross-cylinder'
  | 'fogging'
  | 'binocular'
  | 'stereo'
  | 'motility'
  | 'contrast'
  | 'color'
  | 'filter'

export interface ClinicalTest {
  id: string
  name: string
  category: TestCategory
  template: TestTemplate
  family?: OptotypeFamily
  description: string
}

export const CLINICAL_TESTS: ClinicalTest[] = [
  { id: 'snellen-letras', name: 'Snellen Letras', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'sloan', description: 'Linhas Snellen com letras Sloan.' },
  { id: 'snellen-numeros', name: 'Snellen Números', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'numbers', description: 'Linhas Snellen numéricas.' },
  { id: 'tumbling-e', name: 'Tumbling E', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'tumbling-e', description: 'Optótipo E rotacionável.' },
  { id: 'e-direcional', name: 'E Direcional', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'tumbling-e', description: 'Identificação de orientação do E.' },
  { id: 'landolt-c', name: 'Landolt C', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'landolt-c', description: 'Anel de Landolt com abertura direcional.' },
  { id: 'hotv', name: 'HOTV', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'hotv', description: 'Triagem pediátrica HOTV.' },
  { id: 'lea-symbols', name: 'LEA Symbols', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'lea', description: 'Símbolos pediátricos originais.' },
  { id: 'allen-figures', name: 'Allen Figures', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'allen', description: 'Figuras simples para reconhecimento.' },
  { id: 'sheridan-gardiner', name: 'Sheridan Gardiner', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'gardiner', description: 'Letras isoladas para teste pareado.' },
  { id: 'bailey-lovie', name: 'Bailey-Lovie', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'bailey-lovie', description: 'Progressão logarítmica uniforme.' },
  { id: 'logmar-etdrs', name: 'LogMAR ETDRS', category: 'Tabelas de acuidade visual', template: 'acuity', family: 'etdrs', description: 'Cinco optótipos por linha e passos logMAR.' },
  { id: 'duocromatico', name: 'Duocromático', category: 'Testes de refração', template: 'duochrome', description: 'Campo vermelho-verde para balanceamento refrativo.' },
  { id: 'relogio-astigmatico', name: 'Relógio Astigmático', category: 'Testes de refração', template: 'astigmatic', description: 'Meridianos radiais para astigmatismo.' },
  { id: 'ventilador-astigmatico', name: 'Ventilador Astigmático', category: 'Testes de refração', template: 'astigmatic', description: 'Radiais em leque para comparação de nitidez.' },
  { id: 'cilindro-cruzado', name: 'Cilindro Cruzado', category: 'Testes de refração', template: 'cross-cylinder', description: 'Grade cruzada para refinamento cilíndrico.' },
  { id: 'bicromatico', name: 'Bicromático', category: 'Testes de refração', template: 'duochrome', description: 'Alternativa vermelho-verde.' },
  { id: 'vermelho-verde', name: 'Vermelho-Verde', category: 'Testes de refração', template: 'duochrome', description: 'Comparação de contraste cromático.' },
  { id: 'nevoa-refrativa', name: 'Névoa Refrativa', category: 'Testes de refração', template: 'fogging', description: 'Optótipos suavizados para relaxamento acomodativo.' },
  { id: 'equilibrio-binocular', name: 'Equilíbrio Binocular', category: 'Testes de refração', template: 'binocular', description: 'Comparação simultânea entre olhos.' },
  { id: 'worth-4-pontos', name: 'Worth 4 Pontos', category: 'Testes binoculares', template: 'binocular', description: 'Quatro pontos coloridos para supressão/fusão.' },
  { id: 'vetogramas', name: 'Vetogramas', category: 'Testes binoculares', template: 'binocular', description: 'Alvos pareados para fusão.' },
  { id: 'supressao', name: 'Supressão', category: 'Testes binoculares', template: 'binocular', description: 'Alvos monoculares sobrepostos.' },
  { id: 'fusao', name: 'Fusão', category: 'Testes binoculares', template: 'binocular', description: 'Alvos de fusão central e periférica.' },
  { id: 'vergencia', name: 'Vergência', category: 'Testes binoculares', template: 'binocular', description: 'Escala horizontal para vergências.' },
  { id: 'disparidade-fixacao', name: 'Disparidade de Fixação', category: 'Testes binoculares', template: 'binocular', description: 'Marcadores finos para alinhamento.' },
  { id: 'wirt', name: 'Círculos de Wirt', category: 'Estereopsia', template: 'stereo', description: 'Conjuntos circulares por disparidade.' },
  { id: 'randot', name: 'Randot', category: 'Estereopsia', template: 'stereo', description: 'Padrões de pontos randômicos.' },
  { id: 'fly-test', name: 'Fly Test', category: 'Estereopsia', template: 'stereo', description: 'Figura de mosca estilizada.' },
  { id: 'stereo-shapes', name: 'Stereo Shapes', category: 'Estereopsia', template: 'stereo', description: 'Formas geométricas com deslocamento.' },
  { id: 'h-test', name: 'H Test', category: 'Motilidade ocular', template: 'motility', description: 'Trajeto em H para versões.' },
  { id: 'versoes', name: 'Versões', category: 'Motilidade ocular', template: 'motility', description: 'Alvos cardinais conjugados.' },
  { id: 'duccoes', name: 'Ducções', category: 'Motilidade ocular', template: 'motility', description: 'Alvos monoculares por direção.' },
  { id: 'sacadicos', name: 'Sacádicos', category: 'Motilidade ocular', template: 'motility', description: 'Pontos alternados para sacadas.' },
  { id: 'pursuits', name: 'Pursuits', category: 'Motilidade ocular', template: 'motility', description: 'Linha de seguimento suave.' },
  { id: 'pelli-robson', name: 'Pelli-Robson', category: 'Testes de contraste', template: 'contrast', description: 'Tríades com contraste decrescente.' },
  { id: 'contraste-niveis', name: 'Contraste por níveis', category: 'Testes de contraste', template: 'contrast', description: 'Optótipos em níveis graduais.' },
  { id: 'contraste-senoidal', name: 'Contraste senoidal', category: 'Testes de contraste', template: 'contrast', description: 'Padrão senoidal de frequência espacial.' },
  { id: 'ishihara', name: 'Ishihara', category: 'Testes de cores', template: 'color', description: 'Prancha cromática original inspirada em placas pseudoisocromáticas.' },
  { id: 'hrr', name: 'HRR', category: 'Testes de cores', template: 'color', description: 'Triagem cromática por formas.' },
  { id: 'farnsworth-d15', name: 'Farnsworth D15', category: 'Testes de cores', template: 'color', description: 'Sequência de 15 matizes.' },
  { id: 'farnsworth-100', name: 'Farnsworth 100 Hue', category: 'Testes de cores', template: 'color', description: 'Gradiente de matizes para ordenação.' },
  { id: 'filtro-vermelho', name: 'Vermelho', category: 'Filtros', template: 'filter', description: 'Filtro vermelho em tela cheia.' },
  { id: 'filtro-verde', name: 'Verde', category: 'Filtros', template: 'filter', description: 'Filtro verde em tela cheia.' },
  { id: 'filtro-azul', name: 'Azul', category: 'Filtros', template: 'filter', description: 'Filtro azul em tela cheia.' },
  { id: 'filtro-polarizado', name: 'Polarizado', category: 'Filtros', template: 'filter', description: 'Grade simulada para avaliação polarizada.' },
  { id: 'filtro-anaglifo', name: 'Anáglifo', category: 'Filtros', template: 'filter', description: 'Sobreposição vermelho/ciano.' },
]

export const TEST_CATEGORIES = Array.from(new Set(CLINICAL_TESTS.map((test) => test.category)))
