# Solucao de problemas

## Optotipos.exe nao abre

Verifique:

- a pasta foi copiada inteira;
- `Configuracoes/` existe;
- antivirus nao bloqueou o executavel;
- Windows permitiu executar aplicativo baixado;
- tente abrir como administrador apenas para teste.

## Configurador.exe nao abre

Verifique:

- `Configurador.exe` esta na mesma pasta do pacote portatil;
- `Configuracoes/` existe;
- voce nao moveu apenas o executavel.

## A distancia esta errada

Abra:

```text
Configuracoes/Distancia.txt
```

Correto:

```text
Distancia=4
Unidade=m
```

ou:

```text
Distancia=4000
Unidade=mm
```

Incorreto:

```text
Distancia=4
Unidade=mm
```

## Optotipo 20/20 nao mede o esperado

Refaca:

1. tamanho fisico da tela;
2. resolucao;
3. regua virtual de 100 mm;
4. distancia real;
5. fator de escala.

Valores esperados:

| Distancia | Altura 20/20 |
| --- | ---: |
| 4 m | 5.8178 mm |
| 5 m | 7.2722 mm |
| 6 m | 8.7266 mm |

## Duas telas nao funciona

No Windows:

1. conectar TV/monitor;
2. abrir configuracoes de tela;
3. escolher `Estender estes videos`;
4. confirmar que a TV aparece como segundo monitor;
5. no Configurador, usar:

```text
Modo=DuasTelas
MonitorExaminador=0
MonitorTeste=1
```

## Espelhamento nao funciona

Verifique:

- ha mais de um monitor conectado;
- Windows detectou todos os monitores;
- o modo esta como `Espelhamento`;
- reinicie o `Optotipos.exe` apos mudar cabos/monitores.

## Efeito espelho invertido incorretamente

Abra:

```text
Configuracoes/Inversao.txt
```

Teste combinacoes:

```text
Horizontal=ON
Vertical=OFF
Rotacao=0
```

ou:

```text
Horizontal=OFF
Vertical=ON
Rotacao=0
```

ou:

```text
Horizontal=ON
Vertical=ON
Rotacao=180
```

## Celular nao acessa Wireless

Verifique:

- celular e computador estao no mesmo Wi-Fi;
- nao use `localhost` no celular;
- use o IP mostrado pelo software;
- firewall do Windows permitiu acesso;
- rede esta como privada;
- VPN esta desligada;
- porta 8765 nao esta bloqueada.

Teste no computador:

```text
http://127.0.0.1:8765
```

Teste no celular:

```text
http://IP_DO_COMPUTADOR:8765
```

## Testes Ishihara/HRR/Randot aparecem bloqueados

Isso e esperado se os ativos licenciados nao foram instalados.

Instale em:

```text
Optotipos/Testes/Assets/<test_key>/manifest.json
```

Consulte:

```text
Optotipos/Testes/TESTES_PROFISSIONAIS_LICENCIADOS.md
```

## Relatorio mostra confianca baixa

Possiveis causas:

- medicoes fisicas nao preenchidas;
- erro acima de 2%;
- executaveis nao confirmados sem Python;
- tela unica nao confirmada;
- controle por celular nao testado;
- pacote portatil nao copiado.

Preencha:

```text
Dados/validacao_campo.json
```

Depois rode:

```bat
validar_fase4_windows.bat
```

## Onde ficam os logs

```text
Logs/
```

Arquivos comuns:

```text
Optotipos.txt
Configurador.txt
ValidacaoClinica_Fase4.md
```

## Restaurar configuracao

Use:

```text
Configurador.exe > Backup > Importar Configuracao
```

Arquivo esperado:

```text
BackupCalibracao.opt
```
