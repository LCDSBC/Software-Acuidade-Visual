# Fase 3 - Nucleo clinico profissional

## Implementado nesta fase

- Calibracao clinica revisada:
  - conversao mm -> pixels;
  - conversao pixels -> mm;
  - tamanho de optotipo por distancia;
  - relatorio de precisao estimada;
  - erro maximo estimado;
  - escala aplicada.
- Snellen Letras:
  - linhas 20/400, 20/300, 20/200, 20/100, 20/80, 20/60, 20/50, 20/40, 20/30, 20/25, 20/20, 20/15 e 20/10;
  - desenho vetorial em grade 5x5 para o nucleo de letras;
  - traco proporcional de 1/5 da altura;
  - tamanho calculado por angulo visual de 5 minutos de arco.
- Tumbling E:
  - desenho vetorial em grade 5x5;
  - orientacoes 0, 90, 180 e 270 graus;
  - orientacao aleatoria por linha/simbolo.
- Landolt C:
  - anel com traco proporcional;
  - abertura de 1/5 do diametro;
  - orientacoes 0, 90, 180 e 270 graus.
- LogMAR / ETDRS:
  - progressao logaritmica em passos de 0.1 LogMAR;
  - 5 optotipos por linha;
  - espacamento horizontal e vertical de uma largura/altura de optotipo;
  - rotulos Snellen e LogMAR.
- Duocromatico:
  - fundo vermelho e verde;
  - divisao central;
  - letras calibradas pelo mesmo calculo de optotipo.
- Relogio astigmatico:
  - linhas uniformes cobrindo 180 graus;
  - marcadores a cada 30 graus;
  - contraste configuravel pelo estado de renderizacao.
- Multi-monitor:
  - deteccao de monitores via API nativa do Windows quando disponivel;
  - modo TelaUnica;
  - modo DuasTelas com janela de teste separada;
  - modo Espelhamento com janelas espelhadas em monitores adicionais;
  - troca em tempo real pelo botao "Modo Monitor" ou tecla `M`.

## Testes automatizados

Comando executado:

```bash
python3 -m unittest discover -s tests
```

Resultado:

```text
Ran 28 tests
OK
```

## Cobertura

Comando geral:

```bash
python3 -m coverage run --source=Optotipos/Aplicacao/optotipos_core -m unittest discover -s tests
python3 -m coverage report -m
```

Cobertura total do pacote atual:

```text
TOTAL 54%
```

Motivo: o pacote ainda inclui configurador, wireless, atalhos, empacotamento e renderizadores fora do foco da Fase 3.

Cobertura do nucleo clinico prioritario desta fase:

```bash
python3 -m coverage report -m --include="*/calibration.py,*/rendering.py"
```

Resultado:

```text
calibration.py 100%
rendering.py    98%
TOTAL           99%
```

## Capturas de tela

Nao foram geradas neste ambiente porque o runtime Linux disponivel nao possui `tkinter`.

Validacao grafica final ainda deve ser feita em Windows, apos gerar:

- `Optotipos.exe`
- `Configurador.exe`

## Ainda falta

- Validacao clinica presencial com regua fisica e distancia real.
- Teste do executavel em Windows.
- Teste real com dois monitores fisicos.
- Validacao de luminancia/contraste com equipamento adequado.
- Revisao de fontes/simbolos oficiais para uso comercial quando aplicavel.
