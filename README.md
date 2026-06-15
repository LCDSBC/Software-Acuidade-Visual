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

Depois, copie a pasta `Optotipos/` inteira para pendrive, notebook, desktop ou mini PC.

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
