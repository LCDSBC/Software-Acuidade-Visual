/// <reference types="vite/client" />

type ConfigFileMap = Record<string, string>

interface RuntimeInfo {
  portableRoot: string
  platform: string
  hostname: string
  displays: Array<{
    id: number
    width: number
    height: number
    scaleFactor: number
  }>
}

interface OptotiposBridge {
  readConfigFiles(): Promise<ConfigFileMap>
  writeConfigFiles(files: ConfigFileMap): Promise<{ ok: true; root: string }>
  listProfiles(): Promise<string[]>
  saveProfile(name: string, files: ConfigFileMap): Promise<{ ok: true; name: string }>
  loadProfile(name: string): Promise<ConfigFileMap>
  exportBackup(): Promise<{ ok: true; path: string }>
  importBackup(): Promise<{ ok: true; path: string }>
  openConfigurator(): Promise<{ ok: true; opened: string }>
  requestFullscreen(): Promise<{ ok: true }>
  runtimeInfo(): Promise<RuntimeInfo>
}

interface Window {
  optotiposBridge?: OptotiposBridge
}
