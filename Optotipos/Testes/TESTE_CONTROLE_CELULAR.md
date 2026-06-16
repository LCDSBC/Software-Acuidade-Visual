# Teste do controle pelo celular

## Confirmado automaticamente

O servidor wireless foi testado por HTTP local, simulando um celular acessando:

```text
/
/cmd?key=next
/mirror
```

Arquivo de teste:

```text
tests/test_wireless_control.py
```

Confirmado:

- pagina de controle carrega;
- botoes de comando aparecem;
- comando `next` chega ao callback do software;
- pagina de espelho simples carrega;
- teste atual aparece na pagina;
- servidor inicia e para corretamente;
- `start()` e idempotente enquanto o servidor ja esta rodando.

## Como testar em celular real

1. Conectar computador e celular na mesma rede Wi-Fi.
2. Abrir `Optotipos.exe`.
3. Clicar em `Wireless`.
4. Anotar o endereco exibido, exemplo:

```text
http://192.168.0.50:8765
```

5. Abrir esse endereco no navegador do celular.
6. Testar:

- [ ] Proximo;
- [ ] Anterior;
- [ ] Aumentar;
- [ ] Diminuir;
- [ ] Aleatorio;
- [ ] Fundo;
- [ ] Ocluir E;
- [ ] Ocluir D;
- [ ] Sem oclusao;
- [ ] Modo espelho simples.

## Possiveis problemas

### Celular nao abre o endereco

Verificar:

- computador e celular estao no mesmo Wi-Fi;
- firewall do Windows liberou a rede local;
- a rede nao esta em modo publico bloqueando descoberta;
- VPN nao esta interferindo;
- porta `8765` nao esta bloqueada.

### Comandos nao mudam o teste

Verificar:

- `Optotipos.exe` continua aberto;
- servidor Wireless esta ativo;
- pagina do celular esta usando o endereco correto;
- nenhum outro programa esta usando a porta.

## Status

```text
Confirmado por teste automatizado: SIM
Confirmado em celular fisico: PENDENTE
```

O status so deve ser marcado como final depois do teste em Wi-Fi real.
