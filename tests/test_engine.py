import pytest
from unittest.mock import AsyncMock, patch
from scraper.config import ScraperConfig
from scraper.engine import CanvaScraperEngine

@pytest.mark.asyncio
async def test_fetch_slide_logic():
    config = ScraperConfig("http://fake-url.com", "out.pdf", 1)
    engine = CanvaScraperEngine(config)
    
    mock_page = AsyncMock()
    mock_page.screenshot.return_value = b"fake_image_bytes"
    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    page_num, bytes_res, final_url = await engine._fetch_slide(mock_browser, 1) # <--- DODAJ final_url

    assert page_num == 1
    assert bytes_res == b"fake_image_bytes"

@pytest.mark.asyncio
@patch('scraper.engine.async_playwright')
@patch('scraper.engine.ImageProcessor')
async def test_engine_run_orchestration(mock_processor, mock_playwright):
    """Testuje Integrację (Integration Test) głównej pętli pobierania."""
    config = ScraperConfig("http://fake.com", "out.pdf", total_slides=2)
    engine = CanvaScraperEngine(config)
    
    # Konfiguracja głębokiego mockowania menadżera kontekstu Playwrighta
    mock_pw_context = AsyncMock()
    mock_browser = AsyncMock()
    mock_pw_context.chromium.launch.return_value = mock_browser
    mock_playwright.return_value.__aenter__.return_value = mock_pw_context
    
    # Podmieniamy fizyczne pobieranie (metodę _fetch_slide) żeby od razu zracała fałszywe bajty
    # Używamy side_effect aby dla każdej karty (slajd 1 i slajd 2) zwrócić inną wartość
    engine._fetch_slide = AsyncMock(side_effect=[(1, b"img1", "url#1"), (2, b"img2", "url#2")]) # <--- DODAJ url#1 i url#2
        
    await engine.run()
    
    # Weryfikacja (Asserts) czy wszystko uruchomiło się poprawnie
    assert engine._fetch_slide.call_count == 2
    mock_processor.process_screenshot.assert_called()
    mock_processor.create_pdf.assert_called_once()