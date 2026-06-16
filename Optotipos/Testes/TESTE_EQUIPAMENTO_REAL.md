# Teste em equipamento real

## Status

Este teste nao pode ser concluido dentro do ambiente cloud.

Ele precisa ser executado em:

- computador Windows real;
- monitor, TV ou projetor real;
- regua fisica;
- distancia fisica medida;
- celular na mesma rede Wi-Fi.

## Script assistido

No Windows, dentro da pasta portatil:

```bat
cd Optotipos
teste_equipamento_real_windows.bat
```

O script:

- verifica `Optotipos.exe`;
- verifica `Configurador.exe`;
- cria `Dados/validacao_campo.json` se ainda nao existir;
- gera `Logs/ValidacaoClinica_Fase4.md`;
- abre o JSON de campo para preenchimento;
- abre o relatorio de validacao.

## Equipamentos minimos

- computador Windows;
- monitor/TV/projetor;
- cabo HDMI/DisplayPort adequado;
- regua fisica milimetrada;
- trena ou medidor de distancia;
- celular na mesma rede Wi-Fi;
- ambiente com iluminacao controlada.

## Sequencia de teste

### 1. Identificar equipamento

Preencher em:

```text
Dados/validacao_campo.json
```

Campos:

- operador;
- data;
- modelo do computador;
- versao do Windows;
- GPU/adaptador;
- modelo da TV/monitor;
- resolucao;
- tipo de conexao;
- iluminacao da sala.

### 2. Calibrar

Abrir:

```text
Configurador.exe
```

Validar:

- largura fisica da tela em mm;
- altura fisica da tela em mm;
- resolucao real;
- distancia de exame;
- regua virtual de 100 mm.

Registrar:

```json
"ruler_100mm_measured_mm": 100.0
```

### 3. Medir 20/20

Abrir:

```text
Optotipos.exe
```

Medir a altura do optotipo 20/20 na distancia configurada.

Valores esperados:

| Distancia | Altura 20/20 |
| --- | ---: |
| 4 m | 5.8178 mm |
| 5 m | 7.2722 mm |
| 6 m | 8.7266 mm |

Preencher o campo correspondente:

```json
"optotype_20_20_4m_measured_mm": 5.82
```

### 4. Testar modos de tela

Preencher `true` ou `false`:

```json
"tela_unica_funciona": true,
"duas_telas_funciona": true,
"espelhamento_funciona": true
```

Validar:

- TelaUnica;
- DuasTelas em modo Windows "Estender";
- Espelhamento;
- inversao horizontal;
- inversao vertical;
- tela cheia no monitor de teste.

### 5. Testar celular

Preencher:

```json
"controle_celular_funciona": true
```

Validar:

- celular abre o endereco exibido;
- proximo/anterior;
- aumentar/diminuir;
- oclusao;
- modo espelho simples.

### 6. Testar portabilidade

Copiar a pasta para outro local ou pendrive.

Preencher:

```json
"executaveis_abrem_sem_python": true,
"pacote_portatil_copiado": true,
"configuracoes_persistem": true
```

## Gerar conclusao

Depois de preencher o JSON:

```bat
teste_equipamento_real_windows.bat
```

Revisar:

```text
Logs/ValidacaoClinica_Fase4.md
```

Critério desejado:

```text
Confianca clinica: ALTA
Aprovado para piloto em consultorio: SIM
```

## Se falhar

Nao usar clinicamente enquanto houver:

- erro fisico acima de 2%;
- executavel nao testado sem Python;
- TelaUnica falhando;
- calibracao divergente;
- TV/monitor em resolucao incorreta;
- controle por celular instavel se ele for necessario no fluxo.
