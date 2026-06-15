# Fase 1 - Base e arquitetura portatil

## Objetivo

Definir e validar a fundacao do software antes de evoluir os recursos clinicos.

Esta fase existe para garantir que o projeto tenha:

- escopo claro;
- estrutura portatil;
- dois modulos independentes;
- configuracoes centralizadas;
- ausencia de funcionalidades fora do objetivo clinico;
- caminho de build para `.exe`;
- testes de integridade da arquitetura.

## Escopo do produto

O software e uma aplicacao desktop offline para Windows, destinada exclusivamente a apresentacao de optotipos e testes visuais.

Nao faz parte do produto:

- cadastro de pacientes;
- prontuario eletronico;
- agenda;
- financeiro;
- prescricao;
- armazenamento de dados clinicos pessoais.

## Modulos definidos

### Configurador

Entrada em modo fonte:

```text
Configurador/Configurador.pyw
```

Executavel esperado:

```text
Configurador.exe
```

Responsabilidades:

- calibracao de tela;
- distancia de exame;
- resolucao;
- inversao;
- monitores;
- perfis;
- backup.

### Optotipos

Entrada em modo fonte:

```text
Optotipos/Optotipos.pyw
```

Executavel esperado:

```text
Optotipos.exe
```

Responsabilidades:

- carregar configuracoes salvas;
- abrir em tela cheia quando configurado;
- apresentar testes visuais;
- usar calibracao e perfis ja definidos;
- abrir o configurador quando solicitado.

## Estrutura portatil obrigatoria

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

## Configuracoes obrigatorias

```text
Configuracoes/Tela.txt
Configuracoes/Distancia.txt
Configuracoes/Escala.txt
Configuracoes/Inversao.txt
Configuracoes/Monitores.txt
Configuracoes/Exibicao.txt
Configuracoes/Atalhos.txt
```

Distancia padrao correta:

```text
Distancia=4
Unidade=m
```

Tambem e valido:

```text
Distancia=4000
Unidade=mm
```

Nao e clinicamente valido:

```text
Distancia=4
Unidade=mm
```

## Arquivo de manifesto

A Fase 1 tambem define um manifesto estruturado:

```text
Optotipos/Dados/manifesto_fase1.json
```

Esse arquivo descreve:

- objetivo;
- plataforma alvo;
- modulos;
- fora de escopo;
- pastas obrigatorias;
- arquivos de configuracao obrigatorios;
- criterios de aceite.

## Criterios de aceite

A Fase 1 e considerada completa quando:

- [x] a estrutura portatil existe;
- [x] as configuracoes centrais existem;
- [x] a distancia padrao usa unidade clinica valida;
- [x] os dois pontos de entrada existem;
- [x] o build Windows esta documentado;
- [x] o escopo exclui cadastro, prontuario, agenda e financeiro;
- [x] ha testes automatizados protegendo essa base.

## Testes automatizados relacionados

Arquivo:

```text
tests/test_phase1_foundation.py
```

Validacoes:

- pastas portateis;
- arquivos de configuracao;
- distancia padrao;
- manifesto;
- pontos de entrada;
- script de build Windows;
- ausencia de termos proibidos como modulo de produto.

## Proximas fases

- Fase 2: configurador e armazenamento permanente.
- Fase 3: nucleo clinico profissional.
- Fase 4: validacao clinica e polimento.
