"""Lección 01: inspección explicada del índice MVNS, sin alterar archivos.

Ejecutar desde la raíz del repositorio:
    .venv\\Scripts\\python.exe research\\lessons\\01_mvns.py

La rama de estudio contiene los archivos MVNS y MVNE en research/source_data/.
"""

import argparse
from pathlib import Path
import sys

# Reuse the laboratory reader to avoid diverging parsing rules.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from study_files import read_session  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="KINORYX study 01: source MVNS index")
    parser.add_argument(
        "--session",
        type=Path,
        default=Path("research/source_data/EMG2_Squats.mvns"),
        help="Path to local MVNS index (not a remote URL)",
    )
    args = parser.parse_args()
    if not args.session.is_file():
        parser.error("No encuentro el MVNS. Actualiza esta rama de estudio con git pull.")
    info = read_session(args.session)
    print("=== ESTUDIO 01: MVNS ===")
    print(f"Archivo: {info['file']['name']}")
    print(f"SHA-256: {info['file']['sha256']}")
    print(f"Nombre declarado: {info['session_name']!r}")
    print(f"Comentario: {info['comment']!r}")
    print(f"Archivos referenciados: {len(info['references'])}")
    for i, entry in enumerate(info["references"], start=1):
        print(f"  {i}. {entry['filename']}")
        print(f"     Existe localmente: {entry['exists']}")
        print(f"     timeOffset: {entry['start_offset_as_written']!r}")
        print(f"     timeEndOffset: {entry['end_offset_as_written']!r}")
    print("")
    print("INTERPRETACIÓN: Es un índice de archivos, no una medición de movimiento.")
    print("ATENCIÓN: 'EMG2_Walkig' y 'Squats' discrepan; ejercicio real sin verificar.")
    print("ATENCIÓN: Offset cero no prueba sincronización temporal.")
    print("SIGUIENTE: research/lessons/01_MVNS.md")


if __name__ == "__main__":
    main()
