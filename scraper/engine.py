import asyncio
import logging
import io
from typing import List, Tuple
from PIL import Image
from playwright.async_api import async_playwright, Browser, Page

from scraper.config import ScraperConfig
from scraper.processor import ImageProcessor

logger = logging.getLogger("CanvaScraper")

class CanvaScraperEngine:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)

    async def _fetch_slide(self, browser: Browser, page_num: int) -> Tuple[int, bytes, str]:
        async with self.semaphore:
            logger.info(f"[POBIERANIE] Otwieranie slajdu #{page_num}...")
            
            context = await browser.new_context(
                device_scale_factor=self.config.device_scale_factor
            )
            page = await context.new_page()
            await page.set_viewport_size({
                "width": self.config.viewport_width, 
                "height": self.config.viewport_height
            })
            
            url = f"{self.config.base_url}#{page_num}"
            
            try:
                await page.goto(url, wait_until="load", timeout=self.config.timeout_ms)
                await page.mouse.move(self.config.viewport_width // 2, self.config.viewport_height // 2)
                await page.mouse.move(10, 10)
                
                await page.wait_for_function("""
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images.every(img => img.complete && img.naturalHeight > 0);
                    }
                """, timeout=15000)
                
            except Exception as e:
                logger.warning(f"[{page_num}] Timeout lub blad ladowania: {str(e)}. Wymuszam zrzut.")
            
            await page.wait_for_timeout(self.config.render_wait_ms) 
            
            # --- Czekanie na zniknięcie UI ---
            if self.config.wait_ui_hide_ms > 0:
                # Ruch myszką na samą górę powiadamia, że jesteśmy nieaktywni na dole
                await page.mouse.move(10, 10)
                await page.wait_for_timeout(self.config.wait_ui_hide_ms)
            # ---------------------------------------------

            screenshot_bytes = await page.screenshot()
            final_url = page.url
            await context.close()
            
            logger.info(f"[{page_num}] [OK] Zrzut ekranu pobrany.")
            return page_num, screenshot_bytes, final_url

    def _is_same_slide(self, bytes1: bytes, bytes2: bytes) -> bool:
        try:
            img1 = Image.open(io.BytesIO(bytes1)).resize((16, 16)).convert('L')
            img2 = Image.open(io.BytesIO(bytes2)).resize((16, 16)).convert('L')
            
            pixels1 = list(img1.getdata())
            pixels2 = list(img2.getdata())
            
            diff = sum(abs(p1 - p2) for p1, p2 in zip(pixels1, pixels2)) / len(pixels1)
            return diff < 5.0
        except Exception:
            return False

    async def run(self):
        async with async_playwright() as p:
            logger.info("Uruchamianie przegladarki Chromium...")
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=[
                    "--headless-new",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--mute-audio",
                    "--window-position=-32000,-32000",
                ]
            )
            
            valid_results = []

            if self.config.total_slides > 0:
                tasks = [self._fetch_slide(browser, p) for p in range(1, self.config.total_slides + 1)]
                raw_results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in raw_results:
                    if isinstance(res, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
                        raise res 
                    if isinstance(res, tuple):
                        valid_results.append((res[0], res[1]))
            else:
                logger.info("Wykryto brak zdefiniowanej liczby slajdow. Szukam konca na zywo...")
                current_page = 1
                end_reached = False
                first_slide_bytes = None
                
                while not end_reached:
                    tasks = [self._fetch_slide(browser, current_page + i) for i in range(self.config.max_concurrent)]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for res in batch_results:
                        if isinstance(res, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
                            raise res 

                    ok_results = [r for r in batch_results if isinstance(r, tuple)]
                    ok_results.sort(key=lambda x: x[0])

                    for page_num, screenshot_bytes, final_url in ok_results:
                        if page_num == 1:
                            first_slide_bytes = screenshot_bytes
                            valid_results.append((page_num, screenshot_bytes))
                            continue
                        
                        url_hash = final_url.split("#")[-1] if "#" in final_url else ""
                        is_url_looped = url_hash == "1" or (url_hash.isdigit() and int(url_hash) < page_num)
                        
                        is_visually_looped = False
                        if first_slide_bytes and not is_url_looped:
                            is_visually_looped = self._is_same_slide(first_slide_bytes, screenshot_bytes)
                            
                        if is_url_looped or is_visually_looped:
                            logger.info(f"[STOP] Osiagnieto limit na slajdzie {page_num-1}! (Slajd {page_num} to powtorka)")
                            end_reached = True
                            break
                        
                        valid_results.append((page_num, screenshot_bytes))
                        
                    if not end_reached:
                        current_page += self.config.max_concurrent

            await browser.close()
            
            if valid_results:
                valid_results.sort(key=lambda x: x[0])
                images = [
                    ImageProcessor.process_screenshot(
                        bytes_data, 
                        self.config.viewport_width, 
                        self.config.viewport_height
                    )
                    for _, bytes_data in valid_results
                ]
                ImageProcessor.create_pdf(images, self.config.output_pdf)
            else:
                logger.warning("[BLAD] Nie udalo sie pobrac zadnych prawidlowych slajdow.")