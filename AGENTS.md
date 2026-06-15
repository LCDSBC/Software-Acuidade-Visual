# AGENTS.md

## Cursor Cloud specific instructions

- App de **acuidade visual** (Vite + React 19 + TypeScript). Frontend puro, sem backend nem banco de dados.
- Dependências são instaladas pelo update script (`npm install`). Não é preciso reinstalar manualmente.
- Comandos padrão (ver `package.json`):
  - `npm run dev` — servidor de desenvolvimento (Vite) em `http://localhost:5173`. Use `npm run dev -- --host` para expor na rede.
  - `npm run lint` — ESLint.
  - `npm run build` — type-check (`tsc -b`) + build de produção.
  - `npm run preview` — serve o build de produção.
- Lógica de cálculo da acuidade fica em `src/acuity.ts` (níveis Snellen, tamanho dos optótipos, sorteio de letras). A UI/fluxo fica em `src/App.tsx`.
- Não há testes automatizados configurados ainda; valide mudanças com `npm run lint`, `npm run build` e teste manual no navegador.
