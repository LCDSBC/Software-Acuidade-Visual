import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import {
  ACUITY_LEVELS,
  CLINICAL_TESTS,
  TEST_CATEGORIES,
  generateOptotypes,
  optotypeMetric,
  type ClinicalTest,
  type TestCategory,
} from '../core/acuity'
import { pixelsPerMM, type CalibrationSettings } from '../shared/settings'
import { loadSettings } from '../shared/storage'

export function OptotiposApp() {
  const [settings, setSettings] = useState<CalibrationSettings | null>(null)
  const [category, setCategory] = useState<TestCategory>('Tabelas de acuidade visual')
  const [testIndex, setTestIndex] = useState(0)
  const [toolbarVisible, setToolbarVisible] = useState(true)
  const [seed, setSeed] = useState(2026)

  const tests = useMemo(() => CLINICAL_TESTS.filter((test) => test.category === category), [category])
  const activeTest = tests[testIndex] ?? tests[0]

  useEffect(() => {
    loadSettings().then((loaded) => {
      setSettings(loaded)
      setToolbarVisible(loaded.display.toolbar)
      window.optotiposBridge?.requestFullscreen()
    })
  }, [])

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const isConfigShortcut = event.ctrlKey && event.altKey && event.key.toLowerCase() === 'c'
      if (isConfigShortcut) {
        window.optotiposBridge?.openConfigurator()
      }
      if (event.key === 'f' || event.key === 'F11') {
        setToolbarVisible((current) => !current)
      }
      if (event.key === 'r') {
        setSeed(Date.now())
      }
      if (event.key === 'ArrowRight') {
        setTestIndex((current) => Math.min(tests.length - 1, current + 1))
      }
      if (event.key === 'ArrowLeft') {
        setTestIndex((current) => Math.max(0, current - 1))
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [tests.length])

  if (!settings || !activeTest) {
    return <main className="loading">Carregando optótipos...</main>
  }

  const stageStyle = {
    '--brightness': `${settings.display.brightness}%`,
    '--luminance': `${settings.display.luminance}%`,
    '--stage-background': settings.display.background === 'Branco' ? '#f8fafc' : '#05070d',
    '--stage-foreground': settings.display.background === 'Branco' ? '#05070d' : '#f8fafc',
    transform: [
      `scaleX(${settings.inversion.horizontal ? -1 : 1})`,
      `scaleY(${settings.inversion.vertical ? -1 : 1})`,
      `rotate(${settings.inversion.rotation}deg)`,
    ].join(' '),
    filter: `brightness(${settings.display.brightness}%) ${settings.display.contrastInverted ? 'invert(1)' : ''}`,
  } as CSSProperties

  return (
    <main className="opto-shell">
      {toolbarVisible && (
        <aside className="examiner-panel">
          <div className="brand-row">
            <div className="brand-mark">OP</div>
            <div>
              <h1>Optótipos</h1>
              <p>Perfil: {settings.activeProfile}</p>
            </div>
          </div>

          <label>
            Categoria
            <select
              value={category}
              onChange={(event) => {
                setCategory(event.target.value as TestCategory)
                setTestIndex(0)
              }}
            >
              {TEST_CATEGORIES.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <div className="test-list">
            {tests.map((test, index) => (
              <button key={test.id} className={test.id === activeTest.id ? 'active' : ''} onClick={() => setTestIndex(index)}>
                <strong>{test.name}</strong>
                <small>{test.description}</small>
              </button>
            ))}
          </div>

          <div className="status-grid">
            <span>Distância</span>
            <strong>{(settings.distanceMM / 1000).toFixed(1)} m</strong>
            <span>Escala</span>
            <strong>{pixelsPerMM(settings).toFixed(2)} px/mm</strong>
            <span>Modo</span>
            <strong>{settings.display.mode}</strong>
          </div>

          <div className="shortcut-help">
            <span>CTRL+ALT+C Configurador</span>
            <span>F/F11 barra</span>
            <span>R randomizar</span>
            <span>← → testes</span>
          </div>
        </aside>
      )}

      <section className={toolbarVisible ? 'patient-stage' : 'patient-stage full'} style={stageStyle}>
        <ClinicalTestRenderer test={activeTest} settings={settings} seed={seed} />
      </section>
    </main>
  )
}

function ClinicalTestRenderer({ test, settings, seed }: { test: ClinicalTest; settings: CalibrationSettings; seed: number }) {
  switch (test.template) {
    case 'acuity':
      return <AcuityChart test={test} settings={settings} seed={seed} />
    case 'duochrome':
      return <Duochrome title={test.name} />
    case 'astigmatic':
      return <AstigmaticFan title={test.name} />
    case 'cross-cylinder':
      return <CrossCylinder />
    case 'fogging':
      return <Fogging settings={settings} seed={seed} />
    case 'binocular':
      return <Binocular title={test.name} />
    case 'stereo':
      return <Stereo title={test.name} />
    case 'motility':
      return <Motility title={test.name} />
    case 'contrast':
      return <Contrast title={test.name} settings={settings} seed={seed} />
    case 'color':
      return <ColorTest title={test.name} />
    case 'filter':
      return <FilterTest title={test.name} />
    default:
      return null
  }
}

function AcuityChart({ test, settings, seed }: { test: ClinicalTest; settings: CalibrationSettings; seed: number }) {
  const family = test.family ?? 'sloan'
  return (
    <div className="acuity-chart" aria-label={test.name}>
      <header>
        <h2>{test.name}</h2>
        <p>Snellen · LogMAR · ETDRS · ISO/ANSI</p>
      </header>
      {ACUITY_LEVELS.slice(0, 11).map((level, row) => {
        const metric = optotypeMetric(level.denominator, settings.distanceMM, pixelsPerMM(settings))
        const symbols = generateOptotypes(family, 5, seed + row * 17)
        return (
          <div key={level.snellen20} className={settings.display.lineOcclusion && row > 0 ? 'acuity-row masked' : 'acuity-row'}>
            <span className="line-label">{level.snellen20}</span>
            <div className="line-symbols" style={{ fontSize: `${Math.min(metric.fontSizePx, 180)}px` }}>
              {symbols.map((symbol, index) => (
                <OptotypeSymbol key={`${symbol}-${index}`} symbol={symbol} family={family} index={index} />
              ))}
            </div>
            <span className="line-label">{level.logMAR.toFixed(2)}</span>
          </div>
        )
      })}
    </div>
  )
}

function OptotypeSymbol({ symbol, family, index }: { symbol: string; family: string; index: number }) {
  const rotation = family === 'tumbling-e' || family === 'landolt-c' ? [0, 90, 180, 270][index % 4] : 0
  return (
    <span className={family === 'landolt-c' ? 'landolt-symbol' : 'optotype-symbol'} style={{ transform: `rotate(${rotation}deg)` }}>
      {symbol}
    </span>
  )
}

function Duochrome({ title }: { title: string }) {
  return (
    <div className="duochrome">
      <section>
        <strong>VERMELHO</strong>
        <span>R N D K C</span>
      </section>
      <section>
        <strong>VERDE</strong>
        <span>O S V H Z</span>
      </section>
      <h2>{title}</h2>
    </div>
  )
}

function AstigmaticFan({ title }: { title: string }) {
  return (
    <div className="astigmatic">
      <h2>{title}</h2>
      <div className="radial-clock">
        {Array.from({ length: 12 }, (_, index) => (
          <i key={index} style={{ transform: `rotate(${index * 15}deg)` }} />
        ))}
        <span>+</span>
      </div>
    </div>
  )
}

function CrossCylinder() {
  return (
    <div className="cross-cylinder">
      <h2>Cilindro Cruzado</h2>
      <div className="cross-grid">
        {Array.from({ length: 64 }, (_, index) => (
          <i key={index} />
        ))}
      </div>
    </div>
  )
}

function Fogging({ settings, seed }: { settings: CalibrationSettings; seed: number }) {
  const symbols = generateOptotypes('sloan', 5, seed)
  const metric = optotypeMetric(40, settings.distanceMM, pixelsPerMM(settings))
  return (
    <div className="fogging">
      <h2>Névoa Refrativa</h2>
      <p style={{ fontSize: `${Math.min(metric.fontSizePx, 120)}px` }}>{symbols.join('  ')}</p>
    </div>
  )
}

function Binocular({ title }: { title: string }) {
  return (
    <div className="binocular">
      <h2>{title}</h2>
      <div className="worth">
        <i className="red" />
        <i className="green" />
        <i className="white" />
        <i className="green" />
      </div>
      <div className="fusion-bars">
        <span />
        <span />
      </div>
    </div>
  )
}

function Stereo({ title }: { title: string }) {
  return (
    <div className="stereo">
      <h2>{title}</h2>
      <div className="stereo-grid">
        {Array.from({ length: 36 }, (_, index) => (
          <i key={index} className={index % 7 === 0 ? 'raised' : ''} />
        ))}
      </div>
    </div>
  )
}

function Motility({ title }: { title: string }) {
  return (
    <div className="motility">
      <h2>{title}</h2>
      <svg viewBox="0 0 640 420" role="img" aria-label="Trajeto de motilidade ocular">
        <path d="M110 70 L110 350 M110 210 L530 210 M530 70 L530 350" />
        <circle cx="110" cy="70" r="14" />
        <circle cx="110" cy="210" r="14" />
        <circle cx="110" cy="350" r="14" />
        <circle cx="530" cy="70" r="14" />
        <circle cx="530" cy="210" r="14" />
        <circle cx="530" cy="350" r="14" />
      </svg>
    </div>
  )
}

function Contrast({ title, settings, seed }: { title: string; settings: CalibrationSettings; seed: number }) {
  const symbols = generateOptotypes('sloan', 15, seed)
  return (
    <div className="contrast-test">
      <h2>{title}</h2>
      <div>
        {symbols.map((symbol, index) => (
          <span key={`${symbol}-${index}`} style={{ opacity: Math.max(0.08, 1 - index * 0.06), fontSize: `${42 + pixelsPerMM(settings) * 3}px` }}>
            {symbol}
          </span>
        ))}
      </div>
    </div>
  )
}

function ColorTest({ title }: { title: string }) {
  return (
    <div className="color-test">
      <h2>{title}</h2>
      <div className="color-plate">
        {Array.from({ length: 90 }, (_, index) => (
          <i key={index} className={index % 5 === 0 || index % 11 === 0 ? 'target' : ''} />
        ))}
        <strong>8</strong>
      </div>
    </div>
  )
}

function FilterTest({ title }: { title: string }) {
  const className = title.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replaceAll(' ', '-')
  return (
    <div className={`filter-test ${className}`}>
      <h2>{title}</h2>
      <span>Filtro clínico ativo</span>
    </div>
  )
}
