# Fase 4 - Validacao clinica e polimento

## Objetivo

Transformar o MVP em uma versao testavel em consultorio, sem adicionar novos testes clinicos nesta fase.

O foco e confirmar:

- geracao de `.exe`;
- execucao em Windows sem instalacao complexa;
- portabilidade;
- calibracao fisica;
- multi-monitor;
- TV/monitor externo;
- controle pelo celular;
- registro de precisao clinica.

## Entregas adicionadas

- `Optotipos/ValidacaoClinica.py`
  - gera relatorio de validacao com:
    - status do pacote portatil;
    - status dos executaveis;
    - configuracoes completas;
    - precisao estimada da calibracao;
    - tamanho esperado do optotipo 20/20 em 4 m, 5 m e 6 m;
    - checklist de teste real.
- `Optotipos/validar_fase4_windows.bat`
  - atualiza o relatorio `Logs/ValidacaoClinica_Fase4.md` em ambiente Windows com Python.
- `Optotipos/build_windows.bat`
  - agora roda testes automatizados antes do build;
  - gera `Optotipos.exe` e `Configurador.exe`;
  - cria pacote `dist/Optotipos_Portatil`;
  - gera relatorio inicial de validacao.

## Fluxo recomendado no Windows

### 1. Gerar os executaveis

Em um computador Windows com Python instalado:

```bat
cd Optotipos
build_windows.bat
```

Resultado esperado:

```text
Optotipos/Optotipos.exe
Optotipos/Configurador.exe
Optotipos/dist/Optotipos_Portatil/
Optotipos/Logs/ValidacaoClinica_Fase4.md
```

### 2. Testar portabilidade

Copiar a pasta:

```text
Optotipos/dist/Optotipos_Portatil/
```

para:

- pendrive;
- notebook;
- desktop;
- mini PC.

Confirmar:

- [ ] `Optotipos.exe` abre sem Python instalado;
- [ ] `Configurador.exe` abre sem Python instalado;
- [ ] configuracoes continuam salvas apos fechar e abrir;
- [ ] perfis continuam disponiveis;
- [ ] backup pode ser exportado/importado.

### 3. Calibrar tela/TV

No `Configurador.exe`:

1. informar polegadas;
2. informar largura e altura fisica da tela em mm;
3. informar resolucao real;
4. ajustar a regua virtual de 100 mm com uma regua fisica;
5. salvar o fator de escala;
6. definir distancia como:

```text
Distancia=4
Unidade=m
```

ou:

```text
Distancia=4000
Unidade=mm
```

### 4. Medir optotipo 20/20

Com uma regua fisica, medir a altura total do optotipo 20/20.

Valores esperados:

| Distancia | Altura 20/20 | Espessura do traco |
| --- | ---: | ---: |
| 4 m | 5.8178 mm | 1.1636 mm |
| 5 m | 7.2722 mm | 1.4544 mm |
| 6 m | 8.7266 mm | 1.7453 mm |

Criterio sugerido para MVP clinico:

```text
erro fisico <= 2%
```

### 5. Testar modos de tela

#### Tela unica

- [ ] abrir `Optotipos.exe`;
- [ ] confirmar tela cheia;
- [ ] navegar com teclado;
- [ ] alternar fundo branco/preto;
- [ ] aumentar/diminuir linha.

#### Duas telas

No Windows, conectar TV/monitor como segunda tela.

- [ ] configurar Windows em modo "Estender";
- [ ] selecionar `Modo=DuasTelas`;
- [ ] confirmar painel no monitor principal;
- [ ] confirmar teste visual no segundo monitor/TV;
- [ ] confirmar que os comandos afetam a tela de teste.

#### Espelhamento

- [ ] configurar `Modo=Espelhamento`;
- [ ] confirmar janelas de exibicao nos monitores adicionais;
- [ ] confirmar que proximo/anterior atualiza todas as telas.

### 6. Testar controle por celular

- [ ] computador e celular na mesma rede Wi-Fi;
- [ ] clicar em `Wireless`;
- [ ] abrir o endereco informado no celular;
- [ ] testar proximo/anterior;
- [ ] testar aumentar/diminuir;
- [ ] testar oclusao esquerda/direita;
- [ ] confirmar estabilidade por pelo menos alguns minutos de uso.

## Relatorio final de campo

Preencher em `Logs/ValidacaoClinica_Fase4.md`:

- modelo do monitor/TV;
- resolucao usada;
- distancia real;
- tamanho medido da regua de 100 mm;
- tamanho medido do 20/20;
- erro percentual;
- resultado de tela unica;
- resultado de duas telas;
- resultado de espelhamento;
- resultado do controle por celular.

## Confianca clinica

Para calcular a confianca clinica:

1. copiar `Dados/modelo_validacao_campo.json` para `Dados/validacao_campo.json`;
2. preencher as medicoes fisicas e os checks operacionais;
3. executar `validar_fase4_windows.bat`;
4. revisar a secao `Confianca clinica` em `Logs/ValidacaoClinica_Fase4.md`.

Documento detalhado:

```text
Optotipos/Testes/CONFIANCA_CLINICA.md
```

## Validacao dos optotipos

Antes da medicao fisica, revisar:

```text
Optotipos/Testes/VALIDACAO_CLINICA_OPTOTIPOS.md
```

O relatorio `Logs/ValidacaoClinica_Fase4.md` inclui uma secao automatica de validacao matematica dos optotipos.

## Criterio para concluir a Fase 4

A fase pode ser considerada concluida quando:

- [ ] executaveis gerados em Windows;
- [ ] pacote portatil copiado e executado;
- [ ] calibracao fisica validada;
- [ ] erro do 20/20 dentro do limite definido;
- [ ] tela unica funcionando;
- [ ] duas telas funcionando;
- [ ] espelhamento funcionando;
- [ ] controle por celular funcionando;
- [ ] relatorio de campo preenchido.
- [ ] confianca clinica calculada como alta ou pendencias aceitas formalmente.

## O que nao faz parte desta fase

- adicionar novos testes clinicos;
- implementar Ishihara/HRR/Farnsworth reais;
- implementar prontuario/cadastro;
- alterar escopo para agenda/financeiro;
- certificar o software como dispositivo medico.
