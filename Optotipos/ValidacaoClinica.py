from __future__ import annotations

import argparse
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent / "Aplicacao"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from optotipos_core.paths import ensure_portable_tree  # noqa: E402
from optotipos_core.validation import build_validation_report, write_validation_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera relatorio de validacao clinica e portabilidade.")
    parser.add_argument(
        "--saida",
        default="Logs/ValidacaoClinica_Fase4.md",
        help="Caminho relativo dentro da pasta Optotipos ou caminho absoluto do relatorio.",
    )
    parser.add_argument("--imprimir", action="store_true", help="Tambem imprime o relatorio no console.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = ensure_portable_tree(Path(__file__).resolve().parent)
    destination = Path(args.saida)
    if not destination.is_absolute():
        destination = root / destination

    write_validation_report(destination, root=root)
    if args.imprimir:
        print(build_validation_report(root=root))
    print(f"Relatorio gerado em: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
