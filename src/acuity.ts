// Núcleo de cálculo do teste de acuidade visual.
//
// Baseia-se no padrão do optótipo de Sloan: a linha 20/20 subtende um ângulo
// de 5 minutos de arco no olho do paciente. Uma linha 20/D é (D/20) vezes maior.
// A altura física do optótipo é calculada a partir da distância de teste para
// que o ângulo visual fique correto independentemente do tamanho da tela.

export const SLOAN_LETTERS = ['C', 'D', 'H', 'K', 'N', 'O', 'R', 'S', 'V', 'Z'] as const

export type SloanLetter = (typeof SLOAN_LETTERS)[number]

// 5 minutos de arco em radianos (ângulo subtendido pela linha 20/20).
const ARCMIN_5_RAD = (5 / 60) * (Math.PI / 180)

// Quantidade de optótipos por linha e mínimo de acertos para aprovar a linha.
export const OPTOTYPES_PER_LINE = 5
export const PASS_THRESHOLD = 3

// Denominadores de Snellen (notação 20/D), do maior optótipo para o menor.
const SNELLEN_DENOMINATORS = [200, 100, 70, 50, 40, 30, 25, 20, 15, 13, 10]

export interface AcuityLevel {
  /** Denominador da notação 20/D. */
  denominator: number
  /** Notação imperial, ex.: "20/40". */
  snellen20: string
  /** Notação métrica (6 m), ex.: "6/12". */
  snellen6: string
  /** Acuidade decimal, ex.: 0.5. */
  decimal: number
  /** logMAR (0,0 = visão normal 20/20). */
  logMAR: number
}

export const ACUITY_LEVELS: AcuityLevel[] = SNELLEN_DENOMINATORS.map((d) => ({
  denominator: d,
  snellen20: `20/${d}`,
  snellen6: `6/${Math.round((d * 6) / 20)}`,
  decimal: Math.round((20 / d) * 100) / 100,
  logMAR: Math.round(Math.log10(d / 20) * 100) / 100,
}))

/** Índice padrão para iniciar o teste (linha 20/200, a maior). */
export const START_LEVEL_INDEX = 0

/**
 * Altura física (mm) do optótipo de uma linha, para uma dada distância de teste.
 * @param denominator denominador de Snellen (20/D)
 * @param distanceMeters distância olho–tela em metros
 */
export function optotypeHeightMM(denominator: number, distanceMeters: number): number {
  const distanceMM = distanceMeters * 1000
  const angle = ARCMIN_5_RAD * (denominator / 20)
  return 2 * distanceMM * Math.tan(angle / 2)
}

/**
 * Converte a altura física (mm) em pixels usando a calibração da tela.
 * Aplica o fator de proporção entre altura da maiúscula e font-size (~0,72).
 */
export function optotypeFontSizePx(heightMM: number, pixelsPerMM: number): number {
  const CAP_HEIGHT_RATIO = 0.72
  return (heightMM * pixelsPerMM) / CAP_HEIGHT_RATIO
}

/** Sorteia uma sequência de letras de Sloan, evitando repetição imediata. */
export function randomLetters(count: number): SloanLetter[] {
  const result: SloanLetter[] = []
  for (let i = 0; i < count; i++) {
    let letter: SloanLetter
    do {
      letter = SLOAN_LETTERS[Math.floor(Math.random() * SLOAN_LETTERS.length)]
    } while (result.length > 0 && letter === result[result.length - 1])
    result.push(letter)
  }
  return result
}

export type EyeChoice = 'direito' | 'esquerdo' | 'ambos'

export const EYE_LABELS: Record<EyeChoice, string> = {
  direito: 'Olho direito',
  esquerdo: 'Olho esquerdo',
  ambos: 'Ambos os olhos',
}

/** Largura real de um cartão padrão ISO/IEC 7810 ID-1 (cartão de crédito), em mm. */
export const REFERENCE_CARD_WIDTH_MM = 85.6
