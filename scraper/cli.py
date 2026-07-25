import argparse
import asyncio
import sys
import os
import subprocess
from datetime import datetime
from scraper.config import ScraperConfig, setup_logger
from scraper.engine import CanvaScraperEngine

def run_single(url: str, slides: int, output: str, concurrent: int, debug: bool):
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
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("[STOP] Dzialanie programu zostalo przerwane przez uzytkownika.")
    except Exception as e:
        logger.error(f"[BLAD] Wystapil blad krytyczny: {e}")

def process_batch(filepath: str, concurrent: int, debug: bool):
    logger = setup_logger(debug)
    
    if not os.path.exists(filepath):
        logger.error(f"[BLAD] Plik '{filepath}' nie istnieje.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        line = line.strip()
        
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) < 1:
            continue

        url = parts[0]
        slides = 0
        output = ""
        
        if len(parts) == 2:
            if parts[1].isdigit():
                slides = int(parts[1])
            else:
                output = parts[1]
        elif len(parts) >= 3:
            if parts[1].isdigit():
                slides = int(parts[1])
                output = parts[2]
            else:
                output = parts[1]
                
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"prezentacja_{timestamp}_{i}.pdf"
        
        logger.info(f"\n" + "="*40)
        logger.info(f"[ZADANIE {i}/{len(lines)}] Pobieranie: {output}")
        logger.info("="*40)
        
        config = ScraperConfig(base_url=url, output_pdf=output, total_slides=slides, max_concurrent=concurrent)
        engine = CanvaScraperEngine(config)
        try:
            asyncio.run(engine.run())
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[STOP] Dzialanie programu zostalo przerwane. Konczenie zadan wsadowych.")
            break
        except Exception as e:
            logger.error(f"[BLAD] Blad podczas przetwarzania zadania z linii {i}: {e}")

def main_cli():
    if len(sys.argv) == 1:
        exe_name = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "python main.py"
        
        ps_command = (
            "Clear-Host; "
            "Write-Host '======================================' -ForegroundColor Cyan; "
            "Write-Host '   WITAJ W CANVA SCRAPER CLI!' -ForegroundColor Green; "
            "Write-Host '======================================' -ForegroundColor Cyan; "
            "Write-Host 'System gotowy do przyjmowania komend.'; "
            f"Write-Host 'Wpisz: .\\{exe_name} --help aby zobaczyc instrukcje.' -ForegroundColor Yellow;"
        )
        
        subprocess.Popen(['powershell', '-NoExit', '-Command', ps_command])
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Narzedzie CLI do pobierania slajdow z Canvy.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="Adres URL pojedynczej prezentacji Canva.")
    group.add_argument("--batch", type=str, help="Sciezka do pliku tekstowego z zadaniami.")
    
    parser.add_argument("-s", "--slides", type=int, default=0, help="Liczba slajdow (opcjonalnie).")
    parser.add_argument("-o", "--output", type=str, help="Nazwa pliku PDF (domyslnie z timestampem).")
    parser.add_argument("-c", "--concurrent", type=int, default=3, help="Max jednoczesnych polaczen (domyslnie: 3).")
    parser.add_argument("--debug", action="store_true", help="Wlacza szczegolowe logi.")

    args = parser.parse_args()

    if args.url:
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"prezentacja_{timestamp}.pdf"
            
        run_single(args.url, args.slides, args.output, args.concurrent, args.debug)

    elif args.batch:
        process_batch(args.batch, args.concurrent, args.debug)