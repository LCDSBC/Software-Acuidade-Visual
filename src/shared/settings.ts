export type DisplayMode = 'TelaUnica' | 'DuasTelas' | 'Espelhamento'
export type Rotation = 0 | 90 | 180 | 270
export type BackgroundMode = 'Preto' | 'Branco'

export interface ScreenSettings {
  inches: number
  widthMM: number
  heightMM: number
  resolutionWidth: number
  resolutionHeight: number
}

export interface InversionSettings {
  horizontal: boolean
  vertical: boolean
  rotation: Rotation
}

export interface DisplaySettings {
  mode: DisplayMode
  background: BackgroundMode
  toolbar: boolean
  brightness: number
  luminance: number
  contrastInverted: boolean
  lineOcclusion: boolean
  randomOptotypes: boolean
}

export interface MonitorSettings {
  examinerMonitor: number
  testMonitor: number
}

export interface ShortcutSettings {
  advancedConfig: string
  fullscreen: string
  nextTest: string
  previousTest: string
}

export interface CalibrationSettings {
  screen: ScreenSettings
  distanceMM: number
  scaleFactor: number
  inversion: InversionSettings
  display: DisplaySettings
  monitors: MonitorSettings
  shortcuts: ShortcutSettings
  activeProfile: string
  updatedAt: string
}

export const CONFIG_FILE_NAMES = [
  'Tela.txt',
  'Distancia.txt',
  'Escala.txt',
  'Inversao.txt',
  'Monitores.txt',
  'Exibicao.txt',
  'Atalhos.txt',
] as const

export type ConfigFileName = (typeof CONFIG_FILE_NAMES)[number]
export type ConfigFiles = Record<ConfigFileName, string>

export const DEFAULT_SETTINGS: CalibrationSettings = {
  screen: {
    inches: 27,
    widthMM: 597,
    heightMM: 336,
    resolutionWidth: 1920,
    resolutionHeight: 1080,
  },
  distanceMM: 4000,
  scaleFactor: 1,
  inversion: {
    horizontal: false,
    vertical: false,
    rotation: 0,
  },
  display: {
    mode: 'TelaUnica',
    background: 'Preto',
    toolbar: true,
    brightness: 100,
    luminance: 100,
    contrastInverted: false,
    lineOcclusion: false,
    randomOptotypes: true,
  },
  monitors: {
    examinerMonitor: 1,
    testMonitor: 1,
  },
  shortcuts: {
    advancedConfig: 'CTRL+ALT+C',
    fullscreen: 'F11',
    nextTest: 'ArrowRight',
    previousTest: 'ArrowLeft',
  },
  activeProfile: 'Consultorio_4m.ini',
  updatedAt: new Date(0).toISOString(),
}

function parseKeyValue(content: string): Record<string, string> {
  return Object.fromEntries(
    content
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith('#') && line.includes('='))
      .map((line) => {
        const [key, ...valueParts] = line.split('=')
        return [key.trim(), valueParts.join('=').trim()]
      }),
  )
}

function bool(value: string | undefined, fallback: boolean): boolean {
  if (!value) return fallback
  return ['ON', 'TRUE', 'SIM', '1'].includes(value.toUpperCase())
}

function numberValue(value: string | undefined, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function rotationValue(value: string | undefined): Rotation {
  const parsed = numberValue(value, DEFAULT_SETTINGS.inversion.rotation)
  return parsed === 90 || parsed === 180 || parsed === 270 ? parsed : 0
}

function displayMode(value: string | undefined): DisplayMode {
  return value === 'DuasTelas' || value === 'Espelhamento' ? value : 'TelaUnica'
}

function background(value: string | undefined): BackgroundMode {
  return value === 'Branco' ? 'Branco' : 'Preto'
}

export function serializeSettings(settings: CalibrationSettings): ConfigFiles {
  const screen = settings.screen
  const display = settings.display
  return {
    'Tela.txt': [
      `Polegadas=${screen.inches}`,
      `LarguraTelaMM=${screen.widthMM}`,
      `AlturaTelaMM=${screen.heightMM}`,
      `ResolucaoHorizontal=${screen.resolutionWidth}`,
      `ResolucaoVertical=${screen.resolutionHeight}`,
      `AtualizadoEm=${settings.updatedAt}`,
    ].join('\n'),
    'Distancia.txt': [`Distancia=${settings.distanceMM}`, 'Unidade=mm'].join('\n'),
    'Escala.txt': [
      `FatorEscala=${settings.scaleFactor.toFixed(4)}`,
      `Polegadas=${screen.inches}`,
      `LarguraTelaMM=${screen.widthMM}`,
      `AlturaTelaMM=${screen.heightMM}`,
    ].join('\n'),
    'Inversao.txt': [
      `Horizontal=${settings.inversion.horizontal ? 'ON' : 'OFF'}`,
      `Vertical=${settings.inversion.vertical ? 'ON' : 'OFF'}`,
      `Rotacao=${settings.inversion.rotation}`,
    ].join('\n'),
    'Monitores.txt': [
      `MonitorExaminador=${settings.monitors.examinerMonitor}`,
      `MonitorTeste=${settings.monitors.testMonitor}`,
      `Modo=${display.mode}`,
    ].join('\n'),
    'Exibicao.txt': [
      `Modo=${display.mode}`,
      `Fundo=${display.background}`,
      `BarraFerramentas=${display.toolbar ? 'ON' : 'OFF'}`,
      `Brilho=${display.brightness}`,
      `Luminancia=${display.luminance}`,
      `InversaoContraste=${display.contrastInverted ? 'ON' : 'OFF'}`,
      `OcultacaoLinhas=${display.lineOcclusion ? 'ON' : 'OFF'}`,
      `OptotiposAleatorios=${display.randomOptotypes ? 'ON' : 'OFF'}`,
      `PerfilAtivo=${settings.activeProfile}`,
    ].join('\n'),
    'Atalhos.txt': [
      `ConfiguracoesAvancadas=${settings.shortcuts.advancedConfig}`,
      `TelaCheia=${settings.shortcuts.fullscreen}`,
      `ProximoTeste=${settings.shortcuts.nextTest}`,
      `TesteAnterior=${settings.shortcuts.previousTest}`,
    ].join('\n'),
  }
}

export function parseSettings(files: Partial<Record<ConfigFileName, string>>): CalibrationSettings {
  const tela = parseKeyValue(files['Tela.txt'] ?? '')
  const distancia = parseKeyValue(files['Distancia.txt'] ?? '')
  const escala = parseKeyValue(files['Escala.txt'] ?? '')
  const inversao = parseKeyValue(files['Inversao.txt'] ?? '')
  const monitores = parseKeyValue(files['Monitores.txt'] ?? '')
  const exibicao = parseKeyValue(files['Exibicao.txt'] ?? '')
  const atalhos = parseKeyValue(files['Atalhos.txt'] ?? '')

  const screen = {
    inches: numberValue(tela.Polegadas ?? escala.Polegadas, DEFAULT_SETTINGS.screen.inches),
    widthMM: numberValue(tela.LarguraTelaMM ?? escala.LarguraTelaMM, DEFAULT_SETTINGS.screen.widthMM),
    heightMM: numberValue(tela.AlturaTelaMM ?? escala.AlturaTelaMM, DEFAULT_SETTINGS.screen.heightMM),
    resolutionWidth: numberValue(tela.ResolucaoHorizontal, DEFAULT_SETTINGS.screen.resolutionWidth),
    resolutionHeight: numberValue(tela.ResolucaoVertical, DEFAULT_SETTINGS.screen.resolutionHeight),
  }

  return {
    screen,
    distanceMM: numberValue(distancia.Distancia, DEFAULT_SETTINGS.distanceMM),
    scaleFactor: numberValue(escala.FatorEscala, DEFAULT_SETTINGS.scaleFactor),
    inversion: {
      horizontal: bool(inversao.Horizontal, DEFAULT_SETTINGS.inversion.horizontal),
      vertical: bool(inversao.Vertical, DEFAULT_SETTINGS.inversion.vertical),
      rotation: rotationValue(inversao.Rotacao),
    },
    display: {
      mode: displayMode(exibicao.Modo ?? monitores.Modo),
      background: background(exibicao.Fundo),
      toolbar: bool(exibicao.BarraFerramentas, DEFAULT_SETTINGS.display.toolbar),
      brightness: numberValue(exibicao.Brilho, DEFAULT_SETTINGS.display.brightness),
      luminance: numberValue(exibicao.Luminancia, DEFAULT_SETTINGS.display.luminance),
      contrastInverted: bool(exibicao.InversaoContraste, DEFAULT_SETTINGS.display.contrastInverted),
      lineOcclusion: bool(exibicao.OcultacaoLinhas, DEFAULT_SETTINGS.display.lineOcclusion),
      randomOptotypes: bool(exibicao.OptotiposAleatorios, DEFAULT_SETTINGS.display.randomOptotypes),
    },
    monitors: {
      examinerMonitor: numberValue(monitores.MonitorExaminador, DEFAULT_SETTINGS.monitors.examinerMonitor),
      testMonitor: numberValue(monitores.MonitorTeste, DEFAULT_SETTINGS.monitors.testMonitor),
    },
    shortcuts: {
      advancedConfig: atalhos.ConfiguracoesAvancadas ?? DEFAULT_SETTINGS.shortcuts.advancedConfig,
      fullscreen: atalhos.TelaCheia ?? DEFAULT_SETTINGS.shortcuts.fullscreen,
      nextTest: atalhos.ProximoTeste ?? DEFAULT_SETTINGS.shortcuts.nextTest,
      previousTest: atalhos.TesteAnterior ?? DEFAULT_SETTINGS.shortcuts.previousTest,
    },
    activeProfile: exibicao.PerfilAtivo ?? DEFAULT_SETTINGS.activeProfile,
    updatedAt: tela.AtualizadoEm ?? new Date(0).toISOString(),
  }
}

export function pixelsPerMM(settings: CalibrationSettings): number {
  return (settings.screen.resolutionWidth / settings.screen.widthMM) * settings.scaleFactor
}
