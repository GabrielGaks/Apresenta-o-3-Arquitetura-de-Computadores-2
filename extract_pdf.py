#!/usr/bin/env python3
"""
Extrai texto e imagens de um intervalo de páginas de um PDF.

Uso:
    python3 extract_pdf.py <arquivo.pdf> <pagina_inicio> <pagina_fim>

Saída:
    context.txt  — todo o texto extraído do intervalo
    img/         — todas as imagens extraídas do intervalo
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_tools():
    missing = []
    for tool in ("pdftotext", "pdfimages"):
        result = subprocess.run(["which", tool], capture_output=True)
        if result.returncode != 0:
            missing.append(tool)
    if missing:
        print(f"Erro: ferramentas ausentes: {', '.join(missing)}")
        print("Instale com: sudo apt install poppler-utils")
        sys.exit(1)


def extract_text(pdf_path: str, first: int, last: int, output: str = "context.txt"):
    cmd = [
        "pdftotext",
        "-f", str(first),
        "-l", str(last),
        "-layout",          # preserva layout/colunas
        pdf_path,
        output,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao extrair texto:\n{result.stderr}")
        sys.exit(1)
    size = Path(output).stat().st_size
    print(f"Texto extraído  → {output}  ({size:,} bytes)")


def extract_images(pdf_path: str, first: int, last: int, img_dir: str = "img"):
    os.makedirs(img_dir, exist_ok=True)
    prefix = os.path.join(img_dir, "img")
    cmd = [
        "pdfimages",
        "-f", str(first),
        "-l", str(last),
        "-all",             # mantém formato original (png/jpg/etc)
        pdf_path,
        prefix,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao extrair imagens:\n{result.stderr}")
        sys.exit(1)

    images = list(Path(img_dir).iterdir())
    if images:
        print(f"Imagens extraídas → {img_dir}/  ({len(images)} arquivo(s))")
        for img in sorted(images):
            print(f"   {img.name}")
    else:
        print(f"Nenhuma imagem encontrada nas páginas {first}–{last}.")


def main():
    parser = argparse.ArgumentParser(
        description="Extrai texto e imagens de um PDF para um intervalo de páginas."
    )
    parser.add_argument("pdf", help="Caminho para o arquivo PDF")
    parser.add_argument("inicio", type=int, help="Página inicial (começa em 1)")
    parser.add_argument("fim", type=int, help="Página final (inclusive)")
    parser.add_argument(
        "--saida-texto", default="context.txt",
        help="Arquivo de saída para o texto (padrão: context.txt)"
    )
    parser.add_argument(
        "--saida-imagens", default="img",
        help="Pasta de saída para as imagens (padrão: img/)"
    )
    args = parser.parse_args()

    if not Path(args.pdf).is_file():
        print(f"Erro: arquivo não encontrado: {args.pdf}")
        sys.exit(1)

    if args.inicio < 1:
        print("Erro: a página inicial deve ser >= 1")
        sys.exit(1)

    if args.fim < args.inicio:
        print("Erro: a página final deve ser >= página inicial")
        sys.exit(1)

    check_tools()

    print(f"\nPDF:    {args.pdf}")
    print(f"Páginas: {args.inicio} → {args.fim}\n")

    extract_text(args.pdf, args.inicio, args.fim, args.saida_texto)
    extract_images(args.pdf, args.inicio, args.fim, args.saida_imagens)

    print("\nConcluído.")


if __name__ == "__main__":
    main()
