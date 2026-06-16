# Optotipos Profissional

Software desktop offline e portatil para apresentacao de optotipos e testes visuais em optometria e oftalmologia.

O projeto foi criado do zero e nao inclui cadastro de pacientes, prontuario, agenda ou financeiro. O foco e exclusivamente a realizacao de exames visuais.

## Modulos

- `Optotipos/Optotipos.pyw`: software principal. Carrega as configuracoes, abre em tela cheia e apresenta os testes.
- `Optotipos/Configurador.pyw`: configurador dentro da pasta portatil.
- `Configurador/Configurador.pyw`: entrada independente do modulo configurador.

Ao gerar os executaveis no Windows, o script cria:

- `Optotipos/Optotipos.exe`
- `Optotipos/Configurador.exe`
- `Configurador/Configurador.exe`

## Estrutura portatil

```text
Optotipos/
├── Configuracoes/
├── Perfis/
├── Testes/
├── Dados/
├── Backup/
├── Logs/
├── Aplicacao/
├── Optotipos.pyw
├── Configurador.pyw
└── build_windows.bat
```

Todas as configuracoes usam caminhos relativos e ficam em arquivos `.txt` dentro de `Optotipos/Configuracoes/`.

## Fase 1 - Base e arquitetura

A fundacao do projeto esta documentada em:

```text
Optotipos/Testes/FASE_1_BASE_E_ARQUITETURA.md
```

Manifesto estruturado:

```text
Optotipos/Dados/manifesto_fase1.json
```

Essa fase garante:

- dois modulos independentes;
- estrutura portatil;
- configuracoes centralizadas;
- distancia padrao clinicamente valida;
- ausencia de cadastro, prontuario, agenda e financeiro;
- criterios de aceite testaveis.

## Executar em modo fonte

Requer Python 3.10+.

```bash
python Optotipos/Optotipos.pyw
python Configurador/Configurador.pyw
```

## Gerar `.exe` no Windows

Em um computador Windows com Python instalado:

```bat
cd Optotipos
build_windows.bat
```

O build tambem cria um pacote de teste em:

```text
Optotipos/dist/Optotipos_Portatil/
```

Depois, copie essa pasta para pendrive, notebook, desktop ou mini PC.

## Gerar arquivo baixavel pelo GitHub Actions

Tambem existe uma forma automatica de gerar o pacote Windows em um runner Windows do GitHub.

Workflow:

```text
.github/workflows/build-windows-portable.yml
```

Ele gera o artefato:

```text
Optotipos_Profissional_Windows_Portatil
```

E tambem o instalador:

```text
Optotipos_Profissional_Setup
```

Conteudo esperado:

```text
Optotipos.exe
Configurador.exe
Configuracoes/
Perfis/
Testes/
Dados/
Backup/
Logs/
Manual/
```

Como baixar:

1. abrir a aba `Actions` no GitHub;
2. abrir o workflow `Build Windows Portable Package`;
3. selecionar a execucao mais recente;
4. baixar uma das opcoes:
   - `Optotipos_Profissional_Setup`: instalador tradicional;
   - `Optotipos_Profissional_Windows_Portatil`: pasta portatil;
5. se baixar o instalador, execute `Optotipos_Profissional_Setup.exe`;
6. se baixar o portatil, extraia a pasta e execute `Optotipos.exe`.

## Validacao clinica - Fase 4

Antes de usar em consultorio, siga:

```text
Optotipos/Testes/FASE_4_VALIDACAO_E_POLIMENTO.md
```

Para gerar/atualizar o relatorio tecnico de validacao:

```bat
cd Optotipos
validar_fase4_windows.bat
```

Relatorio gerado:

```text
Optotipos/Logs/ValidacaoClinica_Fase4.md
```

Para calcular a confianca clinica com medicoes reais, copie:

```text
Optotipos/Dados/modelo_validacao_campo.json
```

para:

```text
Optotipos/Dados/validacao_campo.json
```

preencha os valores medidos e execute novamente `validar_fase4_windows.bat`.

Guia:

```text
Optotipos/Testes/CONFIANCA_CLINICA.md
```

Validacao matematica dos optotipos:

```text
Optotipos/Testes/VALIDACAO_CLINICA_OPTOTIPOS.md
```

Testes que exigem ativos licenciados:

```text
Optotipos/Testes/TESTES_PROFISSIONAIS_LICENCIADOS.md
```

Confirmacao multi-monitor:

```text
Optotipos/Testes/CONFIRMACAO_MULTI_MONITOR.md
```

Polimento da interface:

```text
Optotipos/Testes/POLIMENTO_INTERFACE.md
```

Teste do controle pelo celular:

```text
Optotipos/Testes/TESTE_CONTROLE_CELULAR.md
```

Teste em equipamento real:

```text
Optotipos/Testes/TESTE_EQUIPAMENTO_REAL.md
```

## Fase 9 - Manual de uso

Manual principal:

```text
Optotipos/Manual/MANUAL_DE_USO.md
```

Guia rapido:

```text
Optotipos/Manual/GUIA_RAPIDO.md
```

Solucao de problemas:

```text
Optotipos/Manual/SOLUCAO_DE_PROBLEMAS.md
```

## Controles principais

- Seta direita/esquerda: proximo/anterior.
- `+` e `-`: aumenta/diminui o tamanho da linha.
- `R`: alterna apresentacao aleatoria.
- `B`: alterna fundo branco/preto.
- `H` e `V`: espelhamento horizontal/vertical.
- `F`: tela cheia.
- `Ctrl + Alt + C`: abre o configurador.
- Botao `Wireless`: inicia controle remoto por smartphone na rede local.

## Observacao clinica

Antes de uso clinico real, valide a calibracao com regua fisica, distancia de exame, resolucao, luminancia e protocolo da clinica.
