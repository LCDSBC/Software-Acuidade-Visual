import { describe, expect, it } from 'vitest'
import { DEFAULT_SETTINGS, parseSettings, pixelsPerMM, serializeSettings } from './settings'

describe('portable settings files', () => {
  it('serializes settings to the centralized txt files', () => {
    const files = serializeSettings({ ...DEFAULT_SETTINGS, distanceMM: 6000, scaleFactor: 1.0245 })
    expect(files['Distancia.txt']).toContain('Distancia=6000')
    expect(files['Distancia.txt']).toContain('Unidade=mm')
    expect(files['Escala.txt']).toContain('FatorEscala=1.0245')
    expect(Object.keys(files)).toHaveLength(7)
  })

  it('parses saved screen, distance, display, and inversion settings', () => {
    const settings = parseSettings({
      'Tela.txt': 'Polegadas=43\nLarguraTelaMM=941\nAlturaTelaMM=529\nResolucaoHorizontal=3840\nResolucaoVertical=2160',
      'Distancia.txt': 'Distancia=3000\nUnidade=mm',
      'Escala.txt': 'FatorEscala=1.1000',
      'Inversao.txt': 'Horizontal=ON\nVertical=OFF\nRotacao=180',
      'Exibicao.txt': 'Modo=DuasTelas\nFundo=Branco\nBarraFerramentas=OFF\nPerfilAtivo=TV_43pol_3m.ini',
    })

    expect(settings.screen.inches).toBe(43)
    expect(settings.distanceMM).toBe(3000)
    expect(settings.scaleFactor).toBe(1.1)
    expect(settings.inversion).toMatchObject({ horizontal: true, vertical: false, rotation: 180 })
    expect(settings.display.mode).toBe('DuasTelas')
    expect(settings.display.toolbar).toBe(false)
    expect(settings.activeProfile).toBe('TV_43pol_3m.ini')
  })

  it('computes calibrated pixels per millimeter', () => {
    expect(pixelsPerMM(DEFAULT_SETTINGS)).toBeCloseTo(3.216, 3)
  })
})
