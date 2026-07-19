import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from scraper.config import ScraperConfig
from scraper.engine import CanvaScraperEngine

@pytest.mark.asyncio
async def test_fetch_slide_logic():
    """Symulujemy działanie _fetch_slide bez otwierania prawdziwej przeglądarki."""
    config = ScraperConfig("http://fake-url.com", "out.pdf", 1)
    engine = CanvaScraperEngine(config)
    
    # Tworzymy atrapy obiektów Playwrighta
    mock_page = AsyncMock()
    mock_page.screenshot.return_value = b"fake_image_bytes"
    
    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    # Uruchamiamy testowaną metodę
    page_num, bytes_res = await engine._fetch_slide(mock_browser, 1)

    # Weryfikacja
    assert page_num == 1
    assert bytes_res == b"fake_image_bytes"
    mock_page.goto.assert_called_once()
    mock_page.screenshot.assert_called_once()