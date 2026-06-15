import { useEffect, useMemo, useState } from 'react'
import { pixelsPerMM, type CalibrationSettings, type DisplayMode, type Rotation } from '../shared/settings'
import { exportBackup, importBackup, listProfiles, loadProfile, loadSettings, saveProfile, saveSettings } from '../shared/storage'
import { ACUITY_LEVELS, optotypeMetric } from '../core/acuity'

const STEPS = ['Tela', 'Distância', 'Régua virtual', 'Exibição', 'Perfis e backup']

export function ConfiguradorApp() {
  const [settings, setSettings] = useState<CalibrationSettings | null>(null)
  const [step, setStep] = useState(0)
  const [profileName, setProfileName] = useState('Consultorio_4m')
  const [profiles, setProfiles] = useState<string[]>([])
  const [message, setMessage] = useState('')
  const [runtime, setRuntime] = useState<RuntimeInfo | null>(null)

  useEffect(() => {
    loadSettings().then(setSettings)
    listProfiles().then(setProfiles)
    window.optotiposBridge?.runtimeInfo().then(setRuntime)
  }, [])

  const demoMetric = useMemo(() => {
    if (!settings) return null
    return optotypeMetric(20, settings.distanceMM, pixelsPerMM(settings))
  }, [settings])

  if (!settings) {
    return <main className="loading">Carregando configuração...</main>
  }

  function update(next: Partial<CalibrationSettings>) {
    setSettings((current) => (current ? { ...current, ...next } : current))
  }

  async function persist() {
    await saveSettings(settings)
    setMessage('Configurações salvas em Optotipos/Configuracoes.')
  }

  async function persistProfile() {
    const savedName = await saveProfile(profileName, settings)
    const loadedProfiles = await listProfiles()
    setProfiles(loadedProfiles)
    update({ activeProfile: savedName })
    setMessage(`Perfil ${savedName} salvo.`)
  }

  async function applyProfile(name: string) {
    const loaded = await loadProfile(name)
    setSettings(loaded)
    setMessage(`Perfil ${name} carregado.`)
  }

  return (
    <main className="config-shell">
      <aside className="config-sidebar">
        <div className="brand-mark">OP</div>
        <h1>Configurador</h1>
        <p>Calibração portátil para optometria e oftalmologia.</p>
        <nav className="step-list" aria-label="Etapas de calibração">
          {STEPS.map((label, index) => (
            <button key={label} className={index === step ? 'active' : ''} onClick={() => setStep(index)}>
              <span>{index + 1}</span>
              {label}
            </button>
          ))}
        </nav>
      </aside>

      <section className="config-panel">
        <header className="panel-heading">
          <div>
            <p className="eyebrow">Módulo independente</p>
            <h2>{STEPS[step]}</h2>
          </div>
          <button className="primary" onClick={persist}>
            Salvar configuração
          </button>
        </header>

        {step === 0 && (
          <div className="grid two">
            <label className="field-card">
              Tamanho da tela (polegadas)
              <input
                type="number"
                min={10}
                max={120}
                value={settings.screen.inches}
                onChange={(event) => update({ screen: { ...settings.screen, inches: Number(event.target.value) } })}
              />
            </label>
            <label className="field-card">
              Largura física (mm)
              <input
                type="number"
                min={100}
                value={settings.screen.widthMM}
                onChange={(event) => update({ screen: { ...settings.screen, widthMM: Number(event.target.value) } })}
              />
            </label>
            <label className="field-card">
              Altura física (mm)
              <input
                type="number"
                min={80}
                value={settings.screen.heightMM}
                onChange={(event) => update({ screen: { ...settings.screen, heightMM: Number(event.target.value) } })}
              />
            </label>
            <label className="field-card">
              Resolução horizontal
              <input
                type="number"
                min={800}
                value={settings.screen.resolutionWidth}
                onChange={(event) => update({ screen: { ...settings.screen, resolutionWidth: Number(event.target.value) } })}
              />
            </label>
            <label className="field-card">
              Resolução vertical
              <input
                type="number"
                min={600}
                value={settings.screen.resolutionHeight}
                onChange={(event) => update({ screen: { ...settings.screen, resolutionHeight: Number(event.target.value) } })}
              />
            </label>
            <div className="metric-card">
              <span>Escala atual</span>
              <strong>{pixelsPerMM(settings).toFixed(3)} px/mm</strong>
              <small>Aplicada em todos os cálculos de optótipos.</small>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="calibration-block">
            <label className="range-label">
              Distância de exame: <strong>{(settings.distanceMM / 1000).toFixed(1)} m</strong>
            </label>
            <input
              type="range"
              min={1000}
              max={20000}
              step={100}
              value={settings.distanceMM}
              onChange={(event) => update({ distanceMM: Number(event.target.value) })}
            />
            <p>Faixa permitida: 1 a 20 metros. O arquivo `Distancia.txt` é salvo em milímetros.</p>
            {demoMetric && (
              <div className="metric-card wide">
                <span>Optótipo 20/20 calculado</span>
                <strong>{demoMetric.heightMM.toFixed(2)} mm</strong>
                <small>{demoMetric.fontSizePx.toFixed(0)} px na calibração atual.</small>
              </div>
            )}
          </div>
        )}

        {step === 2 && (
          <div className="calibration-block">
            <p>Ajuste a régua virtual até 100 mm medirem exatamente 100 mm na régua física.</p>
            <div className="virtual-ruler" style={{ width: `${100 * pixelsPerMM(settings)}px` }}>
              <span>100 mm</span>
              {Array.from({ length: 11 }, (_, index) => (
                <i key={index} style={{ left: `${index * 10}%` }} />
              ))}
            </div>
            <label className="range-label">
              Fator de escala: <strong>{settings.scaleFactor.toFixed(4)}</strong>
            </label>
            <input
              type="range"
              min={0.5}
              max={1.5}
              step={0.0005}
              value={settings.scaleFactor}
              onChange={(event) => update({ scaleFactor: Number(event.target.value) })}
            />
          </div>
        )}

        {step === 3 && (
          <div className="grid two">
            <label className="field-card">
              Modo de exibição
              <select
                value={settings.display.mode}
                onChange={(event) => update({ display: { ...settings.display, mode: event.target.value as DisplayMode } })}
              >
                <option value="TelaUnica">Tela única</option>
                <option value="DuasTelas">Duas telas</option>
                <option value="Espelhamento">Espelhamento</option>
              </select>
            </label>
            <label className="field-card">
              Fundo
              <select
                value={settings.display.background}
                onChange={(event) => update({ display: { ...settings.display, background: event.target.value === 'Branco' ? 'Branco' : 'Preto' } })}
              >
                <option value="Preto">Preto</option>
                <option value="Branco">Branco</option>
              </select>
            </label>
            <label className="field-card toggle">
              <input
                type="checkbox"
                checked={settings.inversion.horizontal}
                onChange={(event) => update({ inversion: { ...settings.inversion, horizontal: event.target.checked } })}
              />
              Espelhamento horizontal
            </label>
            <label className="field-card toggle">
              <input
                type="checkbox"
                checked={settings.inversion.vertical}
                onChange={(event) => update({ inversion: { ...settings.inversion, vertical: event.target.checked } })}
              />
              Espelhamento vertical
            </label>
            <label className="field-card">
              Rotação
              <select
                value={settings.inversion.rotation}
                onChange={(event) => update({ inversion: { ...settings.inversion, rotation: Number(event.target.value) as Rotation } })}
              >
                {[0, 90, 180, 270].map((rotation) => (
                  <option key={rotation} value={rotation}>
                    {rotation}°
                  </option>
                ))}
              </select>
            </label>
            <label className="field-card">
              Brilho ({settings.display.brightness}%)
              <input
                type="range"
                min={20}
                max={120}
                value={settings.display.brightness}
                onChange={(event) => update({ display: { ...settings.display, brightness: Number(event.target.value) } })}
              />
            </label>
          </div>
        )}

        {step === 4 && (
          <div className="grid two">
            <div className="field-card">
              <label>
                Nome do perfil
                <input value={profileName} onChange={(event) => setProfileName(event.target.value)} />
              </label>
              <button className="primary full" onClick={persistProfile}>
                Salvar perfil
              </button>
            </div>
            <div className="field-card">
              <span>Perfis disponíveis</span>
              <div className="profile-list">
                {profiles.length === 0 && <small>Nenhum perfil salvo ainda.</small>}
                {profiles.map((profile) => (
                  <button key={profile} onClick={() => applyProfile(profile)}>
                    {profile}
                  </button>
                ))}
              </div>
            </div>
            <button className="secondary" onClick={() => exportBackup().then((path) => setMessage(`Backup exportado: ${path}`))}>
              Exportar configuração
            </button>
            <button className="secondary" onClick={() => importBackup().then((path) => setMessage(`Backup importado: ${path}`))}>
              Importar configuração
            </button>
            <div className="metric-card wide">
              <span>Pasta portátil</span>
              <strong>{runtime?.portableRoot ?? 'Optotipos/'}</strong>
              <small>{runtime?.displays.length ?? 1} monitor(es) detectado(s).</small>
            </div>
          </div>
        )}

        <footer className="wizard-actions">
          <button className="secondary" disabled={step === 0} onClick={() => setStep((current) => Math.max(0, current - 1))}>
            Voltar
          </button>
          <button className="secondary" disabled={step === STEPS.length - 1} onClick={() => setStep((current) => Math.min(STEPS.length - 1, current + 1))}>
            Próxima etapa
          </button>
        </footer>

        {message && <p className="toast">{message}</p>}
      </section>
    </main>
  )
}
