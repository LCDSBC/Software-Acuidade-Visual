# Manual de uso - Optotipos Profissional

## 1. Finalidade do software

O Optotipos Profissional e um software desktop offline para Windows destinado a apresentacao de optotipos e testes visuais.

O sistema nao possui:

- cadastro de pacientes;
- prontuario;
- agenda;
- financeiro;
- prescricoes;
- armazenamento de dados pessoais clinicos.

O foco e somente a apresentacao dos testes visuais.

## 2. Modulos

### Optotipos.exe

Modulo principal usado durante o exame.

Funcoes:

- abrir os testes visuais;
- aplicar configuracao salva;
- aplicar distancia;
- aplicar escala;
- aplicar inversao/espelho;
- usar tela cheia;
- controlar apresentacao por teclado, mouse, touch ou celular.

### Configurador.exe

Modulo usado antes do exame.

Funcoes:

- configurar tamanho fisico da tela;
- configurar resolucao;
- configurar distancia;
- calibrar regua de 100 mm;
- configurar monitores;
- configurar inversao horizontal/vertical;
- salvar/carregar perfis;
- exportar/importar backup.

## 3. Estrutura portatil

A pasta portatil deve permanecer inteira:

```text
Optotipos/
├── Optotipos.exe
├── Configurador.exe
├── Configuracoes/
├── Perfis/
├── Testes/
├── Dados/
├── Backup/
├── Logs/
└── Manual/
```

Nao mova somente o `.exe` isoladamente. Copie a pasta completa.

## 4. Primeira execucao

1. Abra `Configurador.exe`.
2. Informe os dados da tela.
3. Informe a distancia do exame.
4. Ajuste a regua virtual com uma regua fisica.
5. Salve as configuracoes.
6. Abra `Optotipos.exe`.
7. Confirme se o teste abre em tela cheia.

## 5. Calibracao da tela

No Configurador, preencher:

- polegadas;
- largura da tela em mm;
- altura da tela em mm;
- resolucao horizontal;
- resolucao vertical.

Depois ajuste a regua virtual de 100 mm ate ela coincidir com uma regua fisica real.

## 6. Distancia de exame

Exemplo recomendado:

```text
Distancia=4
Unidade=m
```

Tambem e valido:

```text
Distancia=4000
Unidade=mm
```

Nao use:

```text
Distancia=4
Unidade=mm
```

porque 4 mm nao e distancia clinica de exame.

## 7. Perfis

Use perfis para salvar configuracoes por ambiente.

Exemplos:

- consultorio 4 m;
- TV 43 pol 3 m;
- projetor 6 m.

No Configurador:

- salvar perfil;
- carregar perfil;
- exportar perfil;
- importar perfil.

## 8. Backup

Use backup antes de trocar de computador ou copiar para pendrive.

Arquivo gerado:

```text
BackupCalibracao.opt
```

Funcoes:

- exportar configuracao;
- importar configuracao.

## 9. Uso do Optotipos.exe

Ao abrir:

- o software carrega as configuracoes;
- aplica o perfil;
- aplica distancia;
- aplica escala;
- aplica inversao;
- abre em tela cheia quando configurado.

Controles principais:

| Acao | Controle |
| --- | --- |
| Proximo teste | Seta direita |
| Teste anterior | Seta esquerda |
| Aumentar linha | + |
| Diminuir linha | - |
| Aleatorio | R |
| Fundo branco/preto | B |
| Espelho horizontal | H |
| Espelho vertical | V |
| Modo monitor | M |
| Tela cheia | F |
| Abrir Configurador | Ctrl + Alt + C |

## 10. Modos de tela

### TelaUnica

Usa uma unica tela para painel e exibicao.

### DuasTelas

Usa:

- monitor 1: painel do examinador;
- monitor 2: exibicao do teste.

No Windows, use preferencialmente o modo:

```text
Estender
```

### Espelhamento

Cria janelas extras nos monitores adicionais.

Use quando precisar exibir em:

- monitor;
- TV;
- projetor.

## 11. Inversao / efeito espelho

Configuracoes:

```text
Horizontal=ON/OFF
Vertical=ON/OFF
Rotacao=0/90/180/270
```

Use quando houver:

- sistema de espelho;
- projetor invertido;
- montagem optica especial.

Sempre confirme visualmente antes do exame.

## 12. Controle pelo celular

1. Computador e celular devem estar na mesma rede Wi-Fi.
2. Abra `Optotipos.exe`.
3. Clique em `Wireless`.
4. Abra no celular o endereco exibido.

Exemplo:

```text
http://192.168.0.50:8765
```

No celular, teste:

- proximo;
- anterior;
- aumentar;
- diminuir;
- aleatorio;
- fundo;
- oclusao;
- modo espelho simples.

## 13. Testes com ativos licenciados

Alguns testes exigem ativos licenciados:

- Ishihara;
- HRR;
- Randot;
- Wirt;
- Fly Test;
- vetogramas;
- polarizados;
- anaglifos.

Sem pacote licenciado, o software bloqueia o uso clinico desses testes.

Instalacao dos ativos:

```text
Optotipos/Testes/Assets/<test_key>/manifest.json
```

Consulte:

```text
Optotipos/Testes/TESTES_PROFISSIONAIS_LICENCIADOS.md
```

## 14. Validacao clinica antes do uso

Antes de usar em consultorio:

1. gerar executaveis;
2. testar em Windows real;
3. calibrar tela/TV;
4. medir regua de 100 mm;
5. medir optotipo 20/20;
6. testar tela unica;
7. testar duas telas;
8. testar espelhamento;
9. testar celular;
10. gerar relatorio.

Roteiro:

```text
Optotipos/Testes/TESTE_EQUIPAMENTO_REAL.md
```

## 15. Relatorio de confianca clinica

Preencha:

```text
Dados/validacao_campo.json
```

Depois rode:

```bat
validar_fase4_windows.bat
```

O relatorio sera salvo em:

```text
Logs/ValidacaoClinica_Fase4.md
```

Resultado esperado:

```text
Confianca clinica: ALTA
Aprovado para piloto em consultorio: SIM
```

## 16. Aviso profissional

Mesmo com confianca alta, o software ainda deve ser usado sob responsabilidade de profissional qualificado.

Validacoes obrigatorias:

- tamanho fisico;
- distancia;
- luminancia;
- contraste;
- cor;
- monitores;
- protocolo da clinica.
