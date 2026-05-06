from __future__ import annotations

import argparse
import base64
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


DEFAULT_BROWSER_PATHS = {
    "chrome": [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ],
    "edge": [
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ],
}


def safe_filename_component(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_value).strip("-._")
    return safe or "slide"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tira uma screenshot de cada slide do HTML e monta um PDF."
    )
    parser.add_argument(
        "--html",
        type=Path,
        default=Path("index.html"),
        help="Arquivo HTML da apresentacao.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("slides-exportados.pdf"),
        help="PDF final gerado.",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=Path("_slides_exportados"),
        help="Pasta temporaria para as imagens.",
    )
    parser.add_argument(
        "--browser",
        choices=("auto", "chrome", "edge"),
        default="auto",
        help="Navegador a usar.",
    )
    parser.add_argument(
        "--browser-binary",
        type=Path,
        default=None,
        help="Caminho completo para o executavel do navegador.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=2560,
        help="Largura da janela usada para as capturas.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1440,
        help="Altura da janela usada para as capturas.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Fator de escala de renderizacao. 2.0 gera capturas bem mais nitidas.",
    )
    parser.add_argument(
        "--settle-ms",
        type=int,
        default=1200,
        help="Tempo de espera apos trocar de slide.",
    )
    parser.add_argument(
        "--keep-images",
        action="store_true",
        help="Mantem as imagens PNG alem do PDF final.",
    )
    parser.add_argument(
        "--pdf-resolution",
        type=float,
        default=600.0,
        help="Mantido para compatibilidade. Com o PDF sem perda, so afeta a escala fisica.",
    )
    parser.add_argument(
        "--pdf-width-in",
        type=float,
        default=13.333,
        help="Largura fisica do PDF em polegadas.",
    )
    parser.add_argument(
        "--pdf-height-in",
        type=float,
        default=7.5,
        help="Altura fisica do PDF em polegadas.",
    )
    return parser.parse_args()


def resolve_browser(browser_name: str, browser_binary: Path | None) -> tuple[str, Path]:
    if browser_binary is not None:
        if not browser_binary.exists():
            raise FileNotFoundError(f"Navegador nao encontrado: {browser_binary}")
        if browser_name == "auto":
            suffix = browser_binary.name.lower()
            if "edge" in suffix:
                browser_name = "edge"
            else:
                browser_name = "chrome"
        return browser_name, browser_binary

    search_order = ["chrome", "edge"] if browser_name == "auto" else [browser_name]
    for candidate_name in search_order:
        for candidate_path in DEFAULT_BROWSER_PATHS[candidate_name]:
            if candidate_path.exists():
                return candidate_name, candidate_path

    raise FileNotFoundError(
        "Nao encontrei Chrome ou Edge instalados. "
        "Use --browser-binary para informar o executavel manualmente."
    )


def build_driver(
    browser_name: str,
    browser_binary: Path,
    width: int,
    height: int,
    scale: float,
):
    common_args = [
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-component-update",
        "--disable-features=MediaRouter,OptimizationHints,AutofillServerCommunication,Translate",
        "--no-first-run",
        "--no-default-browser-check",
        "--log-level=3",
        f"--force-device-scale-factor={scale}",
        "--high-dpi-support=1",
        "--window-size=%d,%d" % (width, height),
        "--allow-file-access-from-files",
    ]

    if browser_name == "chrome":
        options = ChromeOptions()
        options.binary_location = str(browser_binary)
        for arg in common_args:
            options.add_argument(arg)
        return webdriver.Chrome(options=options)

    options = EdgeOptions()
    options.binary_location = str(browser_binary)
    options.use_chromium = True
    for arg in common_args:
        options.add_argument(arg)
    return webdriver.Edge(options=options)


def wait_until_ready(driver) -> None:
    WebDriverWait(driver, 20).until(
        lambda current_driver: current_driver.execute_script("return document.readyState")
        == "complete"
    )
    WebDriverWait(driver, 20).until(
        lambda current_driver: current_driver.execute_script(
            """
            const deck = document.querySelector('deck-stage');
            if (deck) return Boolean(customElements.get('deck-stage') && deck.length > 0);
            return document.querySelectorAll('.slide').length > 0;
            """
        )
    )
    WebDriverWait(driver, 20).until(
        lambda current_driver: current_driver.execute_script(
            "return Array.from(document.images).every(img => img.complete);"
        )
    )


def prepare_page(driver) -> None:
    width = driver.execute_script("return window.innerWidth;")
    height = driver.execute_script("return window.innerHeight;")
    scale = driver.execute_script("return window.devicePixelRatio || 1;")

    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "mobile": False,
            "width": int(width),
            "height": int(height),
            "deviceScaleFactor": scale,
        },
    )
    driver.execute_script(
        """
        const existing = document.getElementById('export-style');
        if (existing) existing.remove();

        const style = document.createElement('style');
        style.id = 'export-style';
        style.textContent = `
          #prog, #counter, #nav-hint {
            display: none !important;
          }
          .slide,
          deck-stage > section,
          .bar-fill,
          .evo-fill,
          .freq-bar,
          .mgr-card,
          #d-c,
          #d-asm {
            transition: none !important;
          }
        `;
        document.head.appendChild(style);
        """
    )
    driver.execute_script(
        """
        window.postMessage({ __omelette_presenting: true }, '*');
        const deck = document.querySelector('deck-stage');
        if (deck && typeof deck.goTo === 'function') deck.goTo(0);
        else if (typeof goTo === 'function') goTo(0);
        """
    )


def collect_slides(driver) -> list[dict[str, str | int]]:
    return driver.execute_script(
        """
        const deck = document.querySelector('deck-stage');
        if (deck) {
          return Array.from(deck.querySelectorAll(':scope > section')).map((slide, index) => ({
            index,
            id: slide.id || slide.getAttribute('data-label') || `slide-${index}`
          }));
        }
        return Array.from(document.querySelectorAll('.slide')).map((slide, index) => ({
          index,
          id: slide.id || `slide-${index}`
        }));
        """
    )


def wait_for_active_slide(driver, slide_id: str) -> None:
    WebDriverWait(driver, 10).until(
        lambda current_driver: current_driver.execute_script(
            """
            const deck = document.querySelector('deck-stage');
            if (deck) {
              const active = deck.querySelector(':scope > section[data-deck-active]');
              return active ? (active.id || active.getAttribute('data-label') || '') : '';
            }
            return document.querySelector('.slide.active')?.id || '';
            """
        )
        == slide_id
    )


def capture_slide(driver, slide_index: int, slide_id: str, output_path: Path, settle_ms: int) -> None:
    driver.execute_script(
        """
        const deck = document.querySelector('deck-stage');
        if (deck && typeof deck.goTo === 'function') deck.goTo(arguments[0]);
        else if (typeof goTo === 'function') goTo(arguments[0]);
        else throw new Error('Nao encontrei API de navegacao dos slides.');
        """,
        slide_index,
    )
    wait_for_active_slide(driver, slide_id)
    time.sleep(settle_ms / 1000)

    if slide_id == "s15":
        driver.execute_script(
            "if (window.runPatch && !window.patchDone) { window.runPatch(); }"
        )
        time.sleep(1.8)

    screenshot = driver.execute_cdp_cmd(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": False,
        },
    )
    output_path.write_bytes(base64.b64decode(screenshot["data"]))


def build_pdf(
    image_paths: list[Path],
    output_pdf: Path,
    resolution: float,
    pdf_width_in: float,
    pdf_height_in: float,
) -> None:
    if not image_paths:
        raise RuntimeError("Nenhuma imagem foi gerada para montar o PDF.")

    page_width = pdf_width_in * 72.0
    page_height = pdf_height_in * 72.0

    pdf = canvas.Canvas(str(output_pdf), pagesize=(page_width, page_height))
    pdf.setTitle(output_pdf.stem)

    for image_path in image_paths:
        reader = ImageReader(str(image_path))
        image_width, image_height = reader.getSize()
        scale = min(page_width / image_width, page_height / image_height)
        draw_width = image_width * scale
        draw_height = image_height * scale
        x = (page_width - draw_width) / 2
        y = (page_height - draw_height) / 2

        pdf.drawImage(
            reader,
            x,
            y,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        pdf.showPage()

    pdf.save()


def main() -> int:
    args = parse_args()

    html_path = args.html.resolve()
    if not html_path.exists():
        print(f"Arquivo HTML nao encontrado: {html_path}", file=sys.stderr)
        return 1

    output_pdf = args.output.resolve()
    images_dir = args.images_dir.resolve()
    images_dir.mkdir(parents=True, exist_ok=True)

    browser_name, browser_binary = resolve_browser(args.browser, args.browser_binary)
    driver = build_driver(
        browser_name,
        browser_binary,
        args.width,
        args.height,
        args.scale,
    )

    image_paths: list[Path] = []
    try:
        driver.get(html_path.as_uri())
        wait_until_ready(driver)
        prepare_page(driver)
        time.sleep(0.5)

        slides = collect_slides(driver)
        total = len(slides)

        print(f"Usando {browser_name}: {browser_binary}")
        print(
            f"Capturando {total} slides de {html_path.name} "
            f"em {args.width}x{args.height} com escala {args.scale}..."
        )

        for slide in slides:
            slide_index = int(slide["index"])
            slide_id = str(slide["id"])
            safe_slide_id = safe_filename_component(slide_id)
            image_path = images_dir / f"{slide_index:02d}-{safe_slide_id}.png"
            capture_slide(driver, slide_index, slide_id, image_path, args.settle_ms)
            image_paths.append(image_path)
            print(f"[{slide_index + 1:02d}/{total:02d}] {image_path.name}")

        build_pdf(
            image_paths,
            output_pdf,
            args.pdf_resolution,
            args.pdf_width_in,
            args.pdf_height_in,
        )
        print(f"PDF criado em: {output_pdf}")
    finally:
        driver.quit()
        if not args.keep_images and images_dir.exists():
            shutil.rmtree(images_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
