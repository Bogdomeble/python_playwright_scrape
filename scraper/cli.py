import argparse
import asyncio
from scraper.config import ScraperConfig, setup_logger
from scraper.engine import CanvaScraperEngine

def parse_arguments() -> argparse.Namespace:
    """Parsuje argumenty przekazane z wiersza poleceń."""
    parser = argparse.ArgumentParser(
        description="Narzędzie CLI do pobierania prezentacji z serwisu Canva i zapisu do pliku PDF."
    )
    
    parser.add_argument("url", type=str, help="Adres URL prezentacji Canva (z /view?embed na końcu).")
    parser.add_argument("-s", "--slides", type=int, required=True, help="Całkowita liczba slajdów do pobrania.")
    parser.add_argument("-o", "--output", type=str, default="prezentacja.pdf", help="Nazwa pliku wyjściowego PDF (domyślnie: prezentacja.pdf).")
    parser.add_argument("-c", "--concurrent", type=int, default=3, help="Maksymalna liczba jednoczesnych połączeń (domyślnie: 3).")
    parser.add_argument("--debug", action="store_true", help="Włącza tryb debugowania (szczegółowe logi).")
    
    return parser.parse_args()

def main_cli():
    """Główny punkt wejścia wywoływany przez skrypt startowy."""
    args = parse_arguments()
    logger = setup_logger(args.debug)
    
    config = ScraperConfig(
        base_url=args.url,
        output_pdf=args.output,
        total_slides=args.slides,
        max_concurrent=args.concurrent
    )
    
    logger.info("Inicjalizacja Canva Scraper CLI...")
    logger.info(f"URL: {config.base_url}")
    logger.info(f"Liczba slajdów: {config.total_slides}")
    
    engine = CanvaScraperEngine(config)
    
    # Uruchomienie asynchronicznej pętli zdarzeń
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        logger.warning("\nPrzerwano działanie programu przez użytkownika (Ctrl+C).")
    except Exception as e:
        logger.error(f"Wystąpił błąd krytyczny: {e}")