# Confianca clinica

## Objetivo

A confianca clinica nao e declarada apenas porque o software abre ou porque os testes automatizados passam.

Ela depende de:

- medicao fisica da calibracao;
- erro real do optotipo;
- funcionamento dos executaveis;
- portabilidade;
- tela unica;
- duas telas;
- espelhamento;
- controle pelo celular;
- persistencia das configuracoes.

## Arquivo de entrada

Copie:

```text
Optotipos/Dados/modelo_validacao_campo.json
```

para:

```text
Optotipos/Dados/validacao_campo.json
```

Depois preencha os valores reais medidos no consultorio.

Exemplo:

```json
{
  "monitor_model": "TV Samsung 43 4K",
  "resolution": "3840x2160",
  "configured_distance_m": 4.0,
  "ruler_100mm_measured_mm": 100.2,
  "optotype_20_20_4m_measured_mm": 5.84,
  "optotype_20_20_5m_measured_mm": null,
  "optotype_20_20_6m_measured_mm": null,
  "checks": {
    "executaveis_abrem_sem_python": true,
    "pacote_portatil_copiado": true,
    "tela_unica_funciona": true,
    "duas_telas_funciona": true,
    "espelhamento_funciona": true,
    "controle_celular_funciona": true,
    "configuracoes_persistem": true
  },
  "notes": "Validado em TV conectada por HDMI."
}
```

## Gerar relatorio

No Windows:

```bat
cd Optotipos
validar_fase4_windows.bat
```

Ou diretamente:

```bat
py ValidacaoClinica.py --entrada-campo Dados\validacao_campo.json --saida Logs\ValidacaoClinica_Fase4.md --imprimir
```

## Pontuacao

A pontuacao e calculada com:

- 55% medicoes fisicas;
- 35% checks operacionais;
- 10% status do pacote portatil.

## Niveis

### Alta

Indica que:

- pontuacao >= 90%;
- medicoes fisicas estao dentro do limite;
- executaveis abrem sem Python;
- tela unica foi confirmada;
- nao ha bloqueios criticos.

Uso recomendado:

```text
apto para piloto em consultorio, ainda com supervisao profissional.
```

### Moderada

Indica que:

- boa parte dos criterios foi cumprida;
- ainda ha pendencias ou checks nao confirmados.

Uso recomendado:

```text
corrigir pendencias antes de uso rotineiro.
```

### Moderada com bloqueios

Indica que a pontuacao pode estar razoavel, mas faltam criterios criticos.

Exemplos:

- executavel nao testado sem Python;
- tela unica nao confirmada;
- pacote incompleto.

### Baixa

Indica que:

- medicao fisica nao foi feita;
- erro fisico passou do limite;
- checks operacionais importantes falharam.

Uso recomendado:

```text
nao usar clinicamente.
```

## Limite de erro

O limite inicial para MVP clinico e:

```text
erro fisico <= 2%
```

Esse limite pode ser ajustado depois com supervisao tecnica/clinica.

## Importante

Mesmo com confianca alta, isto nao substitui:

- validacao clinica formal;
- responsabilidade tecnica;
- avaliacao regulatoria;
- calibracao com instrumentos adequados.
