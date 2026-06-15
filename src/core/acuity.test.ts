import { describe, expect, it } from 'vitest'
import {
  ACUITY_LEVELS,
  CLINICAL_TESTS,
  generateOptotypes,
  optotypeHeightMM,
  optotypeMetric,
} from './acuity'

describe('acuity calculations', () => {
  it('calculates 20/20 optotype height at 4 m from five arc minutes', () => {
    expect(optotypeHeightMM(20, 4000)).toBeCloseTo(5.82, 2)
  })

  it('doubles the physical optotype height when Snellen denominator doubles', () => {
    expect(optotypeHeightMM(40, 4000)).toBeCloseTo(optotypeHeightMM(20, 4000) * 2, 2)
  })

  it('converts calibrated millimeters to renderable pixels and stroke width', () => {
    const metric = optotypeMetric(20, 4000, 3.2)
    expect(metric.fontSizePx).toBeGreaterThan(metric.heightMM)
    expect(metric.strokeWidthPx).toBeGreaterThan(1)
  })

  it('contains standard Snellen, decimal, logMAR, and ETDRS values', () => {
    const level2020 = ACUITY_LEVELS.find((level) => level.denominator === 20)
    expect(level2020).toMatchObject({
      snellen20: '20/20',
      snellen6: '6/6',
      decimal: 1,
      logMAR: 0,
    })
    expect(level2020?.etdrsLetters).toBeGreaterThan(0)
  })

  it('generates deterministic non-repeating optotypes for a family', () => {
    const first = generateOptotypes('sloan', 8, 1234)
    const second = generateOptotypes('sloan', 8, 1234)
    expect(first).toEqual(second)
    for (let index = 1; index < first.length; index += 1) {
      expect(first[index]).not.toBe(first[index - 1])
    }
  })

  it('covers the requested clinical test catalog', () => {
    expect(CLINICAL_TESTS.length).toBeGreaterThanOrEqual(45)
    expect(CLINICAL_TESTS.map((test) => test.name)).toContain('LogMAR ETDRS')
    expect(CLINICAL_TESTS.map((test) => test.name)).toContain('Farnsworth 100 Hue')
    expect(CLINICAL_TESTS.map((test) => test.name)).toContain('Worth 4 Pontos')
  })
})
