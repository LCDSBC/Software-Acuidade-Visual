# Optotipos Profissional

Software desktop portatil para apresentacao de optotipos e testes visuais clinicos.

## Modulos

- `Configurador`: assistente de calibracao, perfis, monitores, inversao e backup.
- `Optotipos`: modulo principal em tela cheia, carregando automaticamente a ultima configuracao.

## Estrutura portatil

```text
Optotipos/
├── Configuracoes/
├── Perfis/
├── Testes/
├── Dados/
├── Backup/
└── Logs/
```

Todas as configuracoes usam caminhos relativos e arquivos texto simples.

## Desenvolvimento

- `npm run dev`: abre o renderer Vite.
- `npm run electron`: abre o shell desktop apontando para o build local.
- `npm run test`: valida calculos e serializacao de configuracoes.
- `npm run lint`: valida TypeScript/React.
- `npm run build`: gera `dist/`.
- `npm run package:win`: gera pacote Windows portatil via Electron Builder.

## Atalhos principais

- `CTRL+ALT+C`: abre configuracoes avancadas.
- `F` ou `F11`: mostra/oculta barra do examinador.
- `R`: randomiza optotipos.
- `Setas esquerda/direita`: navega entre testes.
