import argparse
import asyncio
import sys
import os
import subprocess
from scraper.config import ScraperConfig, setup_logger
from scraper.engine import CanvaScraperEngine

def run_single(url: str, slides: int, output: str, concurrent: int, debug: bool):
    """Pobiera pojedynczą prezentację."""
    logger = setup_logger(debug)
    config = ScraperConfig(
        base_url=url,
        output_pdf=output,
        total_slides=slides,
        max_concurrent=concurrent
    )
    engine = CanvaScraperEngine(config)
    
    try:
        asyncio.run(engine.run())
    except Exception as e:
        logger.error(f"Wystąpił błąd krytyczny: {e}")

def process_batch(filepath: str, concurrent: int, debug: bool):
    """Pobiera wiele prezentacji na podstawie pliku tekstowego."""
    logger = setup_logger(debug)
    
    if not os.path.exists(filepath):
        logger.error(f"❌ Plik '{filepath}' nie istnieje.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        line = line.strip()
        
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) < 2:
            logger.warning(f"⚠️ Pomijam linię {i} - zły format. Wymagane min. URL i LICZBA_SLAJDÓW.")
            continue

        url = parts[0]
        try:
            slides = int(parts[1])
        except ValueError:
            logger.warning(f"⚠️ Pomijam linię {i} - liczba slajdów '{parts[1]}' nie jest prawidłowa.")
            continue

        output = parts[2] if len(parts) > 2 else f"batch_prezentacja_{i}.pdf"
        
        logger.info(f"\n" + "="*40)
        logger.info(f"▶️ [ZADANIE {i}/{len(lines)}] Pobieranie: {output}")
        logger.info("="*40)
        
        config = ScraperConfig(base_url=url, output_pdf=output, total_slides=slides, max_concurrent=concurrent)
        engine = CanvaScraperEngine(config)
        try:
            asyncio.run(engine.run())
        except Exception as e:
            logger.error(f"❌ Błąd podczas przetwarzania zadania z linii {i}: {e}")

def main_cli():
    """Główny punkt wejścia wywoływany przez skrypt startowy."""
    
    # [POPRAWKA] Odporne na błędy wywołanie PowerShella przy dwukliku
    if len(sys.argv) == 1:
        exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "python main.py"
        
        # Używamy złączonych komend PowerShell dla zachowania stabilności
        ps_command = (
            "Clear-Host; "
            "Write-Host '======================================' -ForegroundColor Cyan; "
            "Write-Host '   🚀 WITAJ W CANVA SCRAPER CLI!' -ForegroundColor Green; "
            "Write-Host '======================================' -ForegroundColor Cyan; "
            "Write-Host 'System gotowy do przyjmowania komend.'; "
            f"Write-Host 'Wpisz: .\\{exe_name} --help aby zobaczyc instrukcje.' -ForegroundColor Yellow;"
        )
        
        # Uruchamiamy PowerShell z bezpiecznie sformatowaną komendą
        subprocess.Popen(['powershell', '-NoExit', '-Command', ps_command])
        sys.exit(0)

    # Standardowa logika
    parser = argparse.ArgumentParser(description="Narzędzie CLI do asynchronicznego pobierania slajdów z Canvy.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="Adres URL pojedynczej prezentacji Canva.")
    group.add_argument("--batch", type=str, help="Ścieżka do pliku tekstowego z wieloma zadaniami.")
    
    parser.add_argument("-s", "--slides", type=int, help="Liczba slajdów (wymagane przy --url).")
    parser.add_argument("-o", "--output", type=str, default="prezentacja.pdf", help="Nazwa pliku PDF (domyślnie: prezentacja.pdf).")
    parser.add_argument("-c", "--concurrent", type=int, default=3, help="Max jednoczesnych połączeń (domyślnie: 3).")
    parser.add_argument("--debug", action="store_true", help="Włącza szczegółowe logi.")

    args = parser.parse_args()

    if args.url:
        if not args.slides:
            parser.error("Argument -s/--slides jest wymagany, gdy używasz opcji --url.")
        run_single(args.url, args.slides, args.output, args.concurrent, args.debug)
    elif args.batch:
        process_batch(args.batch, args.concurrent, args.debug)