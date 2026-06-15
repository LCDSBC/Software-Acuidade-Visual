const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('optotiposBridge', {
  readConfigFiles: () => ipcRenderer.invoke('config:read'),
  writeConfigFiles: (files) => ipcRenderer.invoke('config:write', files),
  listProfiles: () => ipcRenderer.invoke('profiles:list'),
  saveProfile: (name, files) => ipcRenderer.invoke('profiles:save', name, files),
  loadProfile: (name) => ipcRenderer.invoke('profiles:load', name),
  exportBackup: () => ipcRenderer.invoke('backup:export'),
  importBackup: () => ipcRenderer.invoke('backup:import'),
  openConfigurator: () => ipcRenderer.invoke('app:open-configurator'),
  requestFullscreen: () => ipcRenderer.invoke('app:fullscreen'),
  runtimeInfo: () => ipcRenderer.invoke('app:runtime-info'),
})
