import asyncio
import logging
from typing import List, Tuple
from playwright.async_api import async_playwright, Browser, Page

from scraper.config import ScraperConfig
from scraper.processor import ImageProcessor

logger = logging.getLogger("CanvaScraper")

class CanvaScraperEngine:
    """Silnik sterujący przeglądarką Chromium poprzez Playwright."""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)

    async def _fetch_slide(self, browser: Browser, page_num: int) -> Tuple[int, bytes]:
        """Pobiera pojedynczy slajd w izolowanym kontekście przeglądarki."""
        async with self.semaphore:
            logger.info(f"[{page_num}/{self.config.total_slides}] Otwieranie slajdu...")
            
            context = await browser.new_context()
            page = await context.new_page()
            await page.set_viewport_size({
                "width": self.config.viewport_width, 
                "height": self.config.viewport_height
            })
            
            url = f"{self.config.base_url}#{page_num}"
            
            try:
                await page.goto(url, wait_until="load", timeout=self.config.timeout_ms)
                # Wybudzenie interfejsu Canvy wirtualną myszką
                await page.mouse.move(self.config.viewport_width // 2, self.config.viewport_height // 2)
                await page.mouse.move(10, 10)
                
                # Dynamiczne oczekiwanie na wyrenderowanie tagów <img>
                await page.wait_for_function("""
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images.every(img => img.complete && img.naturalHeight > 0);
                    }
                """, timeout=15000)
                
            except Exception as e:
                logger.warning(f"[{page_num}] Timeout lub błąd ładowania: {str(e)}. Wymuszam zrzut.")
            
            # Bufor czasowy na renderowanie WebGL przez silnik Canvy
            await page.wait_for_timeout(self.config.render_wait_ms) 
            
            screenshot_bytes = await page.screenshot()
            await context.close()
            
            logger.info(f"[{page_num}/{self.config.total_slides}] ✅ Zrzut ekranu pobrany.")
            return page_num, screenshot_bytes

    async def run(self):
        """Główna orkiestracja pobierania wszystkich slajdów."""
        async with async_playwright() as p:
            logger.info("Uruchamianie przeglądarki Chromium...")
            browser = await p.chromium.launch(
                headless=False, # Flaga headless=False optymalizuje renderowanie WebGL w niektórych środowiskach
                channel="chrome",
                args=[
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--mute-audio"
                ]
            )
            
            tasks = [
                self._fetch_slide(browser, page_num) 
                for page_num in range(1, self.config.total_slides + 1)
            ]
            
            # Zbieramy wyniki współbieżnie
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)
            await browser.close()
            
            # Filtrujemy błędy i sortujemy po numerze strony
            valid_results = [res for res in raw_results if isinstance(res, tuple)]
            valid_results.sort(key=lambda x: x[0])
            
            # Przetwarzanie i łączenie w PDF
            images = [
                ImageProcessor.process_screenshot(
                    bytes_data, 
                    self.config.viewport_width, 
                    self.config.viewport_height
                )
                for _, bytes_data in valid_results
            ]
            
            ImageProcessor.create_pdf(images, self.config.output_pdf)