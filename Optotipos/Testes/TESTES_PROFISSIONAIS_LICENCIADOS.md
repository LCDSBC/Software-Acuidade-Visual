# Testes profissionais licenciados

## Decisao tecnica

Ishihara, HRR, Randot, Wirt, Fly Test, alguns vetogramas e optotipos polarizados/anaglifos podem envolver conteudo proprietario, marcas, pranchas ou desenhos protegidos.

Por isso, o software nao inclui copias desses materiais.

Em vez disso, foi implementado:

- motor de validacao de pacotes licenciados;
- manifesto obrigatorio por teste;
- bloqueio visual quando o pacote nao esta instalado;
- exibicao segura quando o pacote licenciado esta presente;
- relatorio indicando `PRONTO` ou `BLOQUEADO`.

## Testes bloqueados sem ativos licenciados

- Ishihara;
- HRR;
- Circulos de Wirt;
- Randot;
- Fly Test;
- Stereo Shapes;
- Vetogramas;
- Optotipos polarizados;
- Optotipos anaglifos.

## Testes implementados por protocolo sem ativo proprietario

### Pelli-Robson

Implementado como carta de contraste por trios, com contraste descendente.

Ainda exige validacao real de:

- luminancia;
- contraste do monitor;
- distancia;
- iluminacao da sala.

### Farnsworth D15 / 100 Hue

Implementado como organizacao de matizes em sequencia.

Ainda exige validacao real de:

- reproducao cromatica do monitor;
- perfil de cor;
- iluminacao;
- protocolo da clinica.

## Como instalar ativos licenciados

Criar subpasta em:

```text
Optotipos/Testes/Assets/<test_key>/
```

Exemplo para Ishihara:

```text
Optotipos/Testes/Assets/ishihara/
├── manifest.json
├── plate_01.png
├── plate_02.png
└── ...
```

Modelo:

```text
Optotipos/Testes/Assets/manifest.example.json
```

## Chaves aceitas

```text
ishihara
hrr
wirt_circles
randot
fly_test
stereo_shapes
vectograms
polarized_filter
anaglyph_filter
```

## Criterios minimos por pacote

| Teste | Minimo de arquivos | Observacao |
| --- | ---: | --- |
| Ishihara | 24 | placas licenciadas |
| HRR | 14 | placas licenciadas |
| Wirt | 1 | prancha licenciada |
| Randot | 1 | prancha/ativos licenciados |
| Fly Test | 1 | prancha licenciada |
| Stereo Shapes | 1 | ativos licenciados |
| Vetogramas | 1 | vetogramas licenciados |
| Polarizados | 1 | requer hardware/filtros adequados |
| Anaglifos | 1 | requer filtros adequados |

## Relatorio

O relatorio de validacao inclui:

```text
Testes profissionais dependentes de ativos licenciados
```

Cada teste aparece como:

- `PRONTO`: manifesto valido, licenca confirmada, arquivos presentes;
- `BLOQUEADO`: manifesto ausente, licenca nao confirmada ou arquivos faltando.

## Aviso clinico

Mesmo com pacote licenciado instalado, e obrigatorio validar:

- tamanho fisico;
- distancia;
- luminancia;
- contraste;
- reproducao cromatica;
- filtros polarizados/anaglifos;
- protocolo profissional.
