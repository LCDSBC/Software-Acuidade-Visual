# Validacao clinica matematica dos optotipos

## Objetivo

Validar os optotipos prioritarios por criterios matematicos e geometricos antes da medicao fisica em consultorio.

Esta etapa verifica o que o software consegue garantir por codigo:

- proporcao;
- escala;
- angulo visual;
- linhas obrigatorias;
- orientacoes;
- progressao LogMAR;
- espacamento ETDRS;
- dependencia de calibracao.

Ela nao substitui:

- medicao fisica na TV/monitor;
- validacao de luminancia;
- validacao regulatoria;
- avaliacao clinica formal;
- licenciamento de optotipos oficiais/proprietarios.

## Optotipos validados

### Snellen Letras

Validacoes:

- linhas obrigatorias:
  - 20/400;
  - 20/300;
  - 20/200;
  - 20/100;
  - 20/80;
  - 20/60;
  - 20/50;
  - 20/40;
  - 20/30;
  - 20/25;
  - 20/20;
  - 20/15;
  - 20/10.
- altura calculada por 5 minutos de arco;
- traco proporcional de 1/5 da altura;
- desenho vetorial dentro da grade 5x5 para o nucleo de letras.

### Tumbling E

Validacoes:

- grade 5x5;
- haste vertical completa;
- tres barras horizontais completas;
- rotacoes:
  - 0 graus;
  - 90 graus;
  - 180 graus;
  - 270 graus.

### Landolt C

Validacoes:

- abertura proporcional de 1/5;
- traco proporcional;
- orientacoes cardinais.

### LogMAR / ETDRS

Validacoes:

- 5 optotipos por linha;
- progressao de 0.1 LogMAR;
- espacamento horizontal de uma largura de optotipo;
- espacamento vertical de uma altura de optotipo.

### Duocromatico

Validacoes:

- letras usam o mesmo calculo de tamanho dos optotipos;
- traco proporcional 1/5;
- fundo vermelho/verde permanece como validacao visual a ser confirmada em monitor real.

### Relogio astigmatico

Validacoes:

- cobertura de 180 graus;
- linhas uniformes;
- intervalo de 10 graus;
- marcadores principais a cada 30 graus.

## Como gerar o relatorio

O relatorio geral de validacao ja inclui a secao:

```text
Validacao matematica dos optotipos
```

No Windows:

```bat
cd Optotipos
validar_fase4_windows.bat
```

Ou em modo fonte:

```bash
python Optotipos/ValidacaoClinica.py --saida Logs/ValidacaoClinica_Fase4.md --imprimir
```

## Criterio para liberar medicao em campo

Todos os checks criticos devem estar como `OK`.

Depois disso, o software ainda precisa passar pela medicao fisica:

- regua virtual 100 mm;
- optotipo 20/20 na distancia configurada;
- teste em TV/monitor real;
- teste de duas telas;
- teste de espelhamento;
- teste de controle pelo celular.

## Status esperado apos esta validacao

Se todos os criterios matematicos passarem:

```text
Aprovado para validacao de campo: SIM
```

Isso significa:

```text
o nucleo dos optotipos esta matematicamente consistente e pode ser levado para medicao fisica.
```

Nao significa:

```text
software clinicamente certificado ou pronto para uso definitivo sem teste presencial.
```
