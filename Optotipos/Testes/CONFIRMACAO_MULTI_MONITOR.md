# Confirmacao multi-monitor

## O que foi confirmado automaticamente

A logica de layout multi-monitor foi separada em uma funcao testavel:

```text
plan_monitor_layout()
```

Arquivo:

```text
Optotipos/Aplicacao/optotipos_core/main_app.py
```

Testes:

```text
tests/test_monitor_modes.py
```

## Modos confirmados por teste automatizado

### TelaUnica

Confirmado:

- usa o monitor configurado como monitor de teste;
- respeita tela cheia ligada/desligada;
- cria apenas um canvas de exibicao.

### DuasTelas

Confirmado com dois monitores simulados:

- monitor principal fica como painel do examinador;
- segundo monitor recebe janela separada de exibicao;
- janela de teste entra em tela cheia;
- total de canvases: 2.

Fallback confirmado:

- se houver apenas um monitor detectado, volta para `TelaUnica`;
- registra motivo: requer pelo menos dois monitores.

### Espelhamento

Confirmado com tres monitores simulados:

- monitor 1 fica como principal;
- monitores extras recebem janelas `Espelho 1`, `Espelho 2`, etc.;
- cada monitor adicional recebe uma janela de exibicao;
- total de canvases = numero de monitores.

Fallback confirmado:

- se houver apenas um monitor, volta para `TelaUnica`;
- registra motivo: requer monitores adicionais.

## O que ainda precisa ser confirmado fisicamente

Este ambiente nao tem Windows grafico com monitores fisicos conectados.

Ainda precisa validar em campo:

- deteccao real via Windows `EnumDisplayMonitors`;
- TV como segundo monitor HDMI;
- Windows em modo "Estender";
- Windows em modo "Duplicar";
- tela cheia real no monitor de teste;
- coordenadas corretas quando a TV esta a esquerda/direita/acima;
- troca em tempo real pelo botao `Modo Monitor`;
- sincronizacao visual entre janelas espelhadas.

## Como testar no Windows

1. Conectar TV/monitor externo.
2. Configurar Windows em `Estender`.
3. Abrir `Configurador.exe`.
4. Definir:

```text
Modo=DuasTelas
MonitorExaminador=0
MonitorTeste=1
```

5. Abrir `Optotipos.exe`.
6. Confirmar:

- painel no monitor 0;
- optotipos na TV/monitor 1;
- tela cheia no monitor de teste.

Depois testar:

```text
Modo=Espelhamento
```

Confirmar que todas as janelas mudam juntas ao pressionar proximo/anterior.

## Status

```text
Confirmado por teste automatizado: SIM
Confirmado fisicamente em Windows: PENDENTE
```

O status so deve virar final quando o teste em Windows/TV real for preenchido no relatorio de campo.
