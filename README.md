# Software Acuidade Visual

Aplicação web para teste de **acuidade visual** usando optótipos de Sloan.
Apresenta letras em tamanhos decrescentes, registra as respostas e calcula a
acuidade nas notações **Snellen (20/D e 6/D)**, **decimal** e **logMAR**.

> Ferramenta educativa. Não substitui avaliação com oftalmologista.

## Tecnologias

- [Vite](https://vite.dev/) + [React 19](https://react.dev/) + TypeScript
- ESLint para análise estática

## Como rodar (desenvolvimento)

```bash
npm install      # instala dependências
npm run dev      # inicia o servidor de desenvolvimento (http://localhost:5173)
```

Outros scripts:

```bash
npm run lint     # análise estática com ESLint
npm run build    # type-check (tsc -b) + build de produção
npm run preview  # serve o build de produção localmente
```

## Como funciona o teste

1. **Configuração** — escolha o olho avaliado, a distância da tela e calibre o
   tamanho real da tela ajustando a barra à largura de um cartão de crédito
   (85,6 mm, padrão ISO/IEC 7810 ID-1).
2. **Teste** — para cada optótipo apresentado, identifique a letra. O teste
   começa na linha 20/200 e avança para linhas menores enquanto você acerta ao
   menos 3 de 5 letras por linha.
3. **Resultado** — exibe a menor linha aprovada em Snellen, decimal e logMAR.

### Fundamento óptico

A linha 20/20 subtende um ângulo de **5 minutos de arco** no olho do paciente.
Uma linha 20/D é `D/20` vezes maior. A altura física do optótipo é derivada da
distância de teste e convertida em pixels usando a calibração da tela, mantendo
o ângulo visual correto independentemente do tamanho do monitor.

## Estrutura

```
src/
  acuity.ts   # núcleo: níveis Snellen, cálculos de tamanho e sorteio de letras
  App.tsx     # fluxo da aplicação (início → configuração → teste → resultado)
  App.css     # estilos da interface
  index.css   # estilos globais e tema
```
