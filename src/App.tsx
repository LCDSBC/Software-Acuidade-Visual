import { useMemo, useState } from 'react'
import {
  ACUITY_LEVELS,
  EYE_LABELS,
  OPTOTYPES_PER_LINE,
  PASS_THRESHOLD,
  REFERENCE_CARD_WIDTH_MM,
  SLOAN_LETTERS,
  START_LEVEL_INDEX,
  optotypeFontSizePx,
  optotypeHeightMM,
  randomLetters,
  type EyeChoice,
  type SloanLetter,
} from './acuity'
import './App.css'

type Phase = 'home' | 'setup' | 'test' | 'results'

function App() {
  const [phase, setPhase] = useState<Phase>('home')

  // Configuração
  const [eye, setEye] = useState<EyeChoice>('ambos')
  const [distance, setDistance] = useState(3)
  const [cardWidthPx, setCardWidthPx] = useState(320)

  // Estado do teste
  const [levelIndex, setLevelIndex] = useState(START_LEVEL_INDEX)
  const [letters, setLetters] = useState<SloanLetter[]>([])
  const [optotypeIndex, setOptotypeIndex] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const [bestPassedIndex, setBestPassedIndex] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<'acerto' | 'erro' | null>(null)

  const pixelsPerMM = cardWidthPx / REFERENCE_CARD_WIDTH_MM
  const currentLevel = ACUITY_LEVELS[levelIndex]

  const fontSizePx = useMemo(() => {
    const heightMM = optotypeHeightMM(currentLevel.denominator, distance)
    return optotypeFontSizePx(heightMM, pixelsPerMM)
  }, [currentLevel.denominator, distance, pixelsPerMM])

  function startTest() {
    setLevelIndex(START_LEVEL_INDEX)
    setLetters(randomLetters(OPTOTYPES_PER_LINE))
    setOptotypeIndex(0)
    setCorrectCount(0)
    setBestPassedIndex(null)
    setFeedback(null)
    setPhase('test')
  }

  function answer(choice: SloanLetter) {
    const isCorrect = choice === letters[optotypeIndex]
    const newCorrect = correctCount + (isCorrect ? 1 : 0)
    setFeedback(isCorrect ? 'acerto' : 'erro')

    const isLastOptotype = optotypeIndex + 1 >= OPTOTYPES_PER_LINE
    if (!isLastOptotype) {
      setCorrectCount(newCorrect)
      setOptotypeIndex((i) => i + 1)
      return
    }

    // Fim da linha: avalia aprovação e decide próximo passo.
    const passed = newCorrect >= PASS_THRESHOLD
    const nextBest = passed ? levelIndex : bestPassedIndex
    const isSmallestLine = levelIndex + 1 >= ACUITY_LEVELS.length

    if (passed && !isSmallestLine) {
      setBestPassedIndex(nextBest)
      setLevelIndex((i) => i + 1)
      setLetters(randomLetters(OPTOTYPES_PER_LINE))
      setOptotypeIndex(0)
      setCorrectCount(0)
    } else {
      setBestPassedIndex(nextBest)
      setPhase('results')
    }
  }

  const resultLevel = bestPassedIndex !== null ? ACUITY_LEVELS[bestPassedIndex] : null

  return (
    <div className="app">
      <header className="topbar">
        <span className="logo" aria-hidden="true">
          ◉
        </span>
        <div>
          <h1>Acuidade Visual</h1>
          <p className="tagline">Teste de acuidade com optótipos de Sloan</p>
        </div>
      </header>

      {phase === 'home' && (
        <main className="card hero">
          <h2>Avalie sua visão em poucos minutos</h2>
          <p>
            Este teste apresenta optótipos (letras) em tamanhos decrescentes e
            calcula sua acuidade visual nas notações Snellen, decimal e logMAR.
          </p>
          <ul className="bullets">
            <li>Calibre a tela com um cartão padrão</li>
            <li>Informe a distância e o olho avaliado</li>
            <li>Identifique as letras apresentadas</li>
          </ul>
          <button className="primary" onClick={() => setPhase('setup')}>
            Começar
          </button>
          <p className="disclaimer">
            Ferramenta educativa. Não substitui consulta com oftalmologista.
          </p>
        </main>
      )}

      {phase === 'setup' && (
        <main className="card">
          <h2>Configuração do teste</h2>

          <section className="field">
            <label>Olho avaliado</label>
            <div className="segmented">
              {(Object.keys(EYE_LABELS) as EyeChoice[]).map((value) => (
                <button
                  key={value}
                  className={eye === value ? 'seg active' : 'seg'}
                  onClick={() => setEye(value)}
                >
                  {EYE_LABELS[value]}
                </button>
              ))}
            </div>
          </section>

          <section className="field">
            <label htmlFor="distance">
              Distância da tela: <strong>{distance.toFixed(1)} m</strong>
            </label>
            <input
              id="distance"
              type="range"
              min={1}
              max={6}
              step={0.5}
              value={distance}
              onChange={(e) => setDistance(Number(e.target.value))}
            />
          </section>

          <section className="field">
            <label htmlFor="calibration">Calibração da tela</label>
            <p className="hint">
              Ajuste a barra azul até que ela tenha a largura de um cartão de
              crédito real ({REFERENCE_CARD_WIDTH_MM} mm).
            </p>
            <div
              className="calibration-card"
              style={{ width: `${cardWidthPx}px` }}
              data-testid="calibration-card"
            >
              <span>85,60 mm</span>
            </div>
            <input
              id="calibration"
              type="range"
              min={180}
              max={520}
              step={1}
              value={cardWidthPx}
              onChange={(e) => setCardWidthPx(Number(e.target.value))}
            />
            <p className="hint">
              Resolução estimada: <strong>{pixelsPerMM.toFixed(1)} px/mm</strong>
            </p>
          </section>

          <div className="actions">
            <button className="ghost" onClick={() => setPhase('home')}>
              Voltar
            </button>
            <button className="primary" onClick={startTest}>
              Iniciar teste
            </button>
          </div>
        </main>
      )}

      {phase === 'test' && (
        <main className="card test">
          <div className="test-meta">
            <span className="badge">{EYE_LABELS[eye]}</span>
            <span className="badge">Linha {currentLevel.snellen20}</span>
            <span className="badge">
              Letra {optotypeIndex + 1}/{OPTOTYPES_PER_LINE}
            </span>
          </div>

          <div className="optotype-stage">
            <span
              className="optotype"
              data-testid="optotype"
              style={{ fontSize: `${fontSizePx}px` }}
            >
              {letters[optotypeIndex]}
            </span>
          </div>

          {feedback && (
            <p className={`feedback ${feedback}`} data-testid="feedback">
              {feedback === 'acerto' ? 'Correto' : 'Incorreto'}
            </p>
          )}

          <p className="prompt">Qual letra você vê?</p>
          <div className="keypad">
            {SLOAN_LETTERS.map((letter) => (
              <button
                key={letter}
                className="key"
                onClick={() => answer(letter)}
                data-testid={`key-${letter}`}
              >
                {letter}
              </button>
            ))}
          </div>
          <button className="ghost cantsee" onClick={() => answer('_' as SloanLetter)}>
            Não consigo ver
          </button>
        </main>
      )}

      {phase === 'results' && (
        <main className="card results">
          <h2>Resultado</h2>
          <p className="result-eye">{EYE_LABELS[eye]}</p>

          {resultLevel ? (
            <>
              <div className="score" data-testid="score">
                {resultLevel.snellen20}
              </div>
              <div className="score-grid">
                <div>
                  <span className="score-label">Métrico</span>
                  <span className="score-value">{resultLevel.snellen6}</span>
                </div>
                <div>
                  <span className="score-label">Decimal</span>
                  <span className="score-value">
                    {resultLevel.decimal.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="score-label">logMAR</span>
                  <span className="score-value">
                    {resultLevel.logMAR.toFixed(2)}
                  </span>
                </div>
              </div>
              <p className="interpretation">
                {resultLevel.denominator <= 20
                  ? 'Acuidade dentro ou acima do padrão de visão normal (20/20).'
                  : 'Acuidade abaixo do padrão de visão normal. Considere avaliação profissional.'}
              </p>
            </>
          ) : (
            <p className="interpretation">
              Não foi possível identificar a maior linha. Refaça o teste em
              melhores condições de iluminação e distância.
            </p>
          )}

          <div className="actions">
            <button className="ghost" onClick={() => setPhase('setup')}>
              Ajustar configuração
            </button>
            <button className="primary" onClick={startTest}>
              Refazer teste
            </button>
          </div>
        </main>
      )}
    </div>
  )
}

export default App
