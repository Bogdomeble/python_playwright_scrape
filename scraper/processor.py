# scraper/processor.py
import io
import logging
from typing import List, Tuple
from PIL import Image

logger = logging.getLogger("CanvaScraper")

class ImageProcessor:
    """Klasa odpowiedzialna za przetwarzanie zrzutów ekranu i generowanie PDF."""
    
    @staticmethod
    def process_screenshot(screenshot_bytes: bytes, width: int, height: int, crop_bottom: int = 0) -> Image.Image:
        """Konwertuje bajty na obraz PIL i inteligentnie przycina, jeśli zachodzi taka potrzeba."""
        image = Image.open(io.BytesIO(screenshot_bytes)).convert('RGB')
        
        # Jeśli nie żądamy ucinania dolnego paska, po prostu zwracamy CAŁY oryginalny obraz w wysokiej jakości
        if crop_bottom > 0:
            actual_width, actual_height = image.size
            # Wyliczamy skalę, aby poprawnie odciąć dolny pasek niezależnie od device_scale_factor
            scale = actual_height / height 
            scaled_crop = int(crop_bottom * scale)
            
            image = image.crop((0, 0, actual_width, actual_height - scaled_crop))
            
        return image

    @staticmethod
    def create_pdf(images: List[Image.Image], output_path: str) -> None:
        """Łączy listę obiektów Image w jeden plik PDF."""
        if not images:
            logger.warning("Brak obrazów do zapisania. Przerywam generowanie PDF.")
            return

        logger.info(f"Rozpoczynam łączenie {len(images)} slajdów w PDF...")
        try:
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:]
            )
            logger.info(f"✅ Gotowe! Plik zapisano jako: {output_path}")
        except Exception as e:
            logger.error(f"❌ Błąd podczas zapisywania PDF: {e}")
            raise