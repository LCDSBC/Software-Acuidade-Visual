# Guia rapido

## Primeira vez

1. Abra:

```text
Configurador.exe
```

2. Configure:

- tamanho da tela;
- resolucao;
- distancia;
- regua virtual;
- modo de monitor.

3. Salve.

4. Abra:

```text
Optotipos.exe
```

## Configuracao minima recomendada

```text
Distancia=4
Unidade=m
Modo=TelaUnica
Horizontal=OFF
Vertical=OFF
Rotacao=0
```

## Antes do primeiro atendimento

- [ ] medir a regua virtual de 100 mm;
- [ ] medir o optotipo 20/20;
- [ ] testar tela cheia;
- [ ] testar atalhos;
- [ ] testar backup;
- [ ] salvar perfil do consultorio;
- [ ] gerar relatorio de validacao.

## Atalhos essenciais

| Tecla | Acao |
| --- | --- |
| Direita | Proximo |
| Esquerda | Anterior |
| + | Aumentar |
| - | Diminuir |
| R | Aleatorio |
| B | Fundo branco/preto |
| H | Espelho horizontal |
| V | Espelho vertical |
| M | Modo monitor |
| F | Tela cheia |
| Ctrl + Alt + C | Configurador |

## Teste com celular

1. Clique em `Wireless`.
2. Abra no celular o endereco exibido.
3. Teste proximo/anterior.

## Relatorio de campo

No Windows:

```bat
teste_equipamento_real_windows.bat
```

Preencha:

```text
Dados/validacao_campo.json
```

Resultado:

```text
Logs/ValidacaoClinica_Fase4.md
```
