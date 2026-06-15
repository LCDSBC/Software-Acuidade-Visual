const { app, BrowserWindow, ipcMain, screen } = require('electron')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { execFile, spawn } = require('node:child_process')

const CONFIG_FILES = [
  'Tela.txt',
  'Distancia.txt',
  'Escala.txt',
  'Inversao.txt',
  'Monitores.txt',
  'Exibicao.txt',
  'Atalhos.txt',
]

const PORTABLE_DIRS = ['Configuracoes', 'Perfis', 'Testes', 'Dados', 'Backup', 'Logs']

function portableRoot() {
  if (!app.isPackaged) {
    return path.join(process.cwd(), 'Optotipos')
  }

  const exeDir = path.dirname(process.execPath)
  const bundled = path.join(process.resourcesPath, 'Optotipos')
  const sibling = path.join(exeDir, 'Optotipos')
  return fs.existsSync(sibling) ? sibling : bundled
}

function ensurePortableTree() {
  const root = portableRoot()
  fs.mkdirSync(root, { recursive: true })
  for (const dir of PORTABLE_DIRS) {
    fs.mkdirSync(path.join(root, dir), { recursive: true })
  }
  return root
}

function configDir() {
  return path.join(ensurePortableTree(), 'Configuracoes')
}

function readConfigFiles() {
  const dir = configDir()
  return Object.fromEntries(
    CONFIG_FILES.map((file) => {
      const fullPath = path.join(dir, file)
      return [file, fs.existsSync(fullPath) ? fs.readFileSync(fullPath, 'utf8') : '']
    }),
  )
}

function writeConfigFiles(files) {
  const dir = configDir()
  for (const file of CONFIG_FILES) {
    if (typeof files[file] === 'string') {
      fs.writeFileSync(path.join(dir, file), files[file], 'utf8')
    }
  }
  return { ok: true, root: portableRoot() }
}

function modeFromExecutable() {
  const exeName = path.basename(process.execPath).toLowerCase()
  if (process.env.OPTOTIPOS_MODE === 'configurador' || exeName.includes('configurador')) {
    return 'configurador'
  }
  return 'optotipos'
}

function appUrl(mode) {
  const hash = mode === 'configurador' ? '#/configurador' : '#/optotipos'
  if (process.env.VITE_DEV_SERVER_URL) {
    return `${process.env.VITE_DEV_SERVER_URL}/${hash}`
  }
  return `file://${path.join(__dirname, '..', 'dist', 'index.html')}${hash}`
}

function createWindow(mode = modeFromExecutable()) {
  ensurePortableTree()
  const primary = screen.getPrimaryDisplay()
  const win = new BrowserWindow({
    title: mode === 'configurador' ? 'Configurador' : 'Optótipos Profissional',
    width: mode === 'configurador' ? 1280 : primary.bounds.width,
    height: mode === 'configurador' ? 860 : primary.bounds.height,
    fullscreen: mode === 'optotipos',
    autoHideMenuBar: true,
    backgroundColor: '#05070d',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })
  win.loadURL(appUrl(mode))
  return win
}

function createShortcut() {
  if (process.platform !== 'win32' || !app.isPackaged) {
    return
  }

  const desktop = app.getPath('desktop')
  const shortcut = path.join(desktop, 'Optótipos Profissional.lnk')
  if (fs.existsSync(shortcut)) {
    return
  }

  const script = `
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut('${shortcut.replaceAll("'", "''")}')
    $shortcut.TargetPath = '${process.execPath.replaceAll("'", "''")}'
    $shortcut.WorkingDirectory = '${path.dirname(process.execPath).replaceAll("'", "''")}'
    $shortcut.Save()
  `
  execFile('powershell.exe', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script])
}

app.whenReady().then(() => {
  createShortcut()
  createWindow()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

ipcMain.handle('config:read', () => readConfigFiles())
ipcMain.handle('config:write', (_event, files) => writeConfigFiles(files))

ipcMain.handle('profiles:list', () => {
  const dir = path.join(ensurePortableTree(), 'Perfis')
  return fs
    .readdirSync(dir)
    .filter((file) => file.endsWith('.ini'))
    .sort((a, b) => a.localeCompare(b, 'pt-BR'))
})

ipcMain.handle('profiles:save', (_event, name, files) => {
  const safeName = String(name).replace(/[^a-z0-9_-]/gi, '_') || 'Perfil'
  const fullPath = path.join(ensurePortableTree(), 'Perfis', `${safeName}.ini`)
  fs.writeFileSync(fullPath, JSON.stringify(files, null, 2), 'utf8')
  return { ok: true, name: path.basename(fullPath) }
})

ipcMain.handle('profiles:load', (_event, name) => {
  const fullPath = path.join(ensurePortableTree(), 'Perfis', path.basename(String(name)))
  return JSON.parse(fs.readFileSync(fullPath, 'utf8'))
})

ipcMain.handle('backup:export', () => {
  const backupPath = path.join(ensurePortableTree(), 'Backup', 'BackupCalibracao.opt')
  const payload = {
    exportedAt: new Date().toISOString(),
    files: readConfigFiles(),
  }
  fs.writeFileSync(backupPath, JSON.stringify(payload, null, 2), 'utf8')
  return { ok: true, path: backupPath }
})

ipcMain.handle('backup:import', () => {
  const backupPath = path.join(ensurePortableTree(), 'Backup', 'BackupCalibracao.opt')
  const payload = JSON.parse(fs.readFileSync(backupPath, 'utf8'))
  writeConfigFiles(payload.files)
  return { ok: true, path: backupPath }
})

ipcMain.handle('app:open-configurator', () => {
  if (app.isPackaged) {
    const candidate = path.join(path.dirname(process.execPath), 'Configurador.exe')
    if (fs.existsSync(candidate)) {
      spawn(candidate, [], { detached: true, stdio: 'ignore' }).unref()
      return { ok: true, opened: candidate }
    }
  }
  createWindow('configurador')
  return { ok: true, opened: 'internal-window' }
})

ipcMain.handle('app:fullscreen', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender)
  win?.setFullScreen(true)
  return { ok: true }
})

ipcMain.handle('app:runtime-info', () => ({
  portableRoot: portableRoot(),
  platform: process.platform,
  hostname: os.hostname(),
  displays: screen.getAllDisplays().map((display) => ({
    id: display.id,
    width: display.bounds.width,
    height: display.bounds.height,
    scaleFactor: display.scaleFactor,
  })),
}))
