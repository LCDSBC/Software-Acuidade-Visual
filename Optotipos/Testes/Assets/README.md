# Ativos clinicos licenciados

Esta pasta e reservada para conteudo clinico que depende de licenca, fabricante ou material proprietario.

Nao inclua aqui copias nao autorizadas de:

- Ishihara;
- HRR;
- Randot;
- Wirt;
- Fly Test;
- vetogramas comerciais;
- optotipos polarizados/anaglifos proprietarios.

## Estrutura esperada

Cada teste deve ter uma subpasta:

```text
Assets/
├── ishihara/
│   ├── manifest.json
│   ├── plate_01.png
│   └── ...
├── hrr/
├── randot/
├── wirt_circles/
├── fly_test/
├── stereo_shapes/
├── vectograms/
├── polarized_filter/
└── anaglyph_filter/
```

## Manifesto obrigatorio

Cada subpasta precisa de um `manifest.json`.

Use `manifest.example.json` como modelo.

Campos obrigatorios:

- `license.licensed`: deve ser `true`;
- `source`: origem/licenciante;
- `version`: versao do pacote;
- `files`: lista de arquivos presentes.

Sem manifesto valido, o teste fica bloqueado para uso clinico.
