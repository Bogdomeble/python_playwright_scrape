from dataclasses import dataclass
import logging
import os
from datetime import datetime

@dataclass
class ScraperConfig:
    """Klasa przechowująca konfigurację pobierania."""
    base_url: str
    output_pdf: str
    total_slides: int = 0
    max_concurrent: int = 3
    timeout_ms: int = 60000
    render_wait_ms: int = 8000
    viewport_width: int = 1920
    viewport_height: int = 1080

    device_scale_factor: float = 2.0 # skalowanie obrazu

def setup_logger(debug: bool = False) -> logging.Logger:
    """Konfiguruje globalny system logowania (konsola + plik tekstowy)."""
    logger = logging.getLogger("CanvaScraper")
    
    # Zapobiega duplikowaniu logów przy pętli batch (czyszczenie starych handlerów)
    if logger.hasHandlers():
        logger.handlers.clear()
        
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    # 1. Wypisywanie w konsoli
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # 2. Zapisywanie do pliku
    os.makedirs("logs", exist_ok=True)
    # Logi nazywamy dzisiejszą datą, żeby wszystkie zadania z danego dnia były w jednym pliku
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join("logs", f"scraper_{date_str}.log")
    
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger