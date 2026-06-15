import {
  CONFIG_FILE_NAMES,
  DEFAULT_SETTINGS,
  parseSettings,
  serializeSettings,
  type CalibrationSettings,
  type ConfigFileName,
  type ConfigFiles,
} from './settings'

const STORAGE_KEY = 'optotipos-profissional-config'

function normalizeFiles(files: Record<string, string>): ConfigFiles {
  const defaults = serializeSettings(DEFAULT_SETTINGS)
  return Object.fromEntries(
    CONFIG_FILE_NAMES.map((fileName) => [fileName, files[fileName] ?? defaults[fileName]]),
  ) as ConfigFiles
}

export async function loadSettings(): Promise<CalibrationSettings> {
  if (window.optotiposBridge) {
    const files = await window.optotiposBridge.readConfigFiles()
    const normalized = normalizeFiles(files)
    await window.optotiposBridge.writeConfigFiles(normalized)
    return parseSettings(normalized)
  }

  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    await saveSettings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS
  }
  return parseSettings(normalizeFiles(JSON.parse(raw)))
}

export async function saveSettings(settings: CalibrationSettings): Promise<ConfigFiles> {
  const stamped = { ...settings, updatedAt: new Date().toISOString() }
  const files = serializeSettings(stamped)
  if (window.optotiposBridge) {
    await window.optotiposBridge.writeConfigFiles(files)
  } else {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(files))
  }
  return files
}

export async function listProfiles(): Promise<string[]> {
  if (window.optotiposBridge) {
    return window.optotiposBridge.listProfiles()
  }
  return Object.keys(window.localStorage)
    .filter((key) => key.startsWith(`${STORAGE_KEY}:profile:`))
    .map((key) => key.replace(`${STORAGE_KEY}:profile:`, ''))
}

export async function saveProfile(name: string, settings: CalibrationSettings): Promise<string> {
  const fileName = name.endsWith('.ini') ? name : `${name}.ini`
  const files = serializeSettings({ ...settings, activeProfile: fileName, updatedAt: new Date().toISOString() })
  if (window.optotiposBridge) {
    const result = await window.optotiposBridge.saveProfile(fileName.replace(/\.ini$/, ''), files)
    return result.name
  }
  window.localStorage.setItem(`${STORAGE_KEY}:profile:${fileName}`, JSON.stringify(files))
  return fileName
}

export async function loadProfile(name: string): Promise<CalibrationSettings> {
  if (window.optotiposBridge) {
    const files = await window.optotiposBridge.loadProfile(name)
    await window.optotiposBridge.writeConfigFiles(files)
    return parseSettings(normalizeFiles(files as Partial<Record<ConfigFileName, string>>))
  }
  const raw = window.localStorage.getItem(`${STORAGE_KEY}:profile:${name}`)
  if (!raw) {
    throw new Error(`Perfil ${name} não encontrado.`)
  }
  const files = normalizeFiles(JSON.parse(raw))
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(files))
  return parseSettings(files)
}

export async function exportBackup(): Promise<string> {
  if (window.optotiposBridge) {
    const result = await window.optotiposBridge.exportBackup()
    return result.path
  }
  return 'BackupCalibracao.opt salvo no armazenamento local do navegador.'
}

export async function importBackup(): Promise<string> {
  if (window.optotiposBridge) {
    const result = await window.optotiposBridge.importBackup()
    return result.path
  }
  return 'Importação de backup disponível no aplicativo desktop.'
}
