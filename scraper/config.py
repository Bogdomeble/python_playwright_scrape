from dataclasses import dataclass
import logging

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
    """Konfiguruje globalny system logowania (rejestrowania zdarzeń)."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger("CanvaScraper")