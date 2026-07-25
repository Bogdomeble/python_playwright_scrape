# scraper/processor.py
import io
import logging
from typing import List, Tuple
from PIL import Image

logger = logging.getLogger("CanvaScraper")

class ImageProcessor:
    @staticmethod
    def process_screenshot(screenshot_bytes: bytes, width: int, height: int, crop_bottom: int = 0) -> Image.Image:
        image = Image.open(io.BytesIO(screenshot_bytes)).convert('RGB')
        
        if crop_bottom > 0:
            actual_width, actual_height = image.size
            scale = actual_height / height 
            scaled_crop = int(crop_bottom * scale)
            
            image = image.crop((0, 0, actual_width, actual_height - scaled_crop))
            
        return image

    @staticmethod
    def create_pdf(images: List[Image.Image], output_path: str) -> None:
        if not images:
            logger.warning("Brak obrazow do zapisania. Przerywam generowanie PDF.")
            return

        logger.info(f"Rozpoczynam laczenie {len(images)} slajdow w PDF...")
        try:
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:]
            )
            logger.info(f"[SUKCES] Gotowe! Plik zapisano jako: {output_path}")
        except Exception as e:
            logger.error(f"[BLAD] Blad podczas zapisywania PDF: {e}")
            raise