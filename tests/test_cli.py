# tests/test_cli.py
import pytest
import logging
from unittest.mock import patch
from scraper.cli import process_batch

def test_process_batch_valid_file(tmp_path, caplog):
    """Test sprawdza czy parser wsadowy poprawnie czyta plik txt omijając komentarze."""
    
    # KROK 1: Mówimy Pytestowi, aby łapał również standardowe logi informacyjne (INFO)
    caplog.set_level(logging.INFO)
    
    # KROK 2: Używamy czystego łączenia stringów zamiast potrójnego cudzysłowu.
    # W ten sposób dokładnie wiemy, że plik ma równo 4 fizyczne linijki.
    batch_file = tmp_path / "lista.txt"
    batch_content = (
        "# To jest komentarz\n"
        "https://fake.canva.com/1 5 out1.pdf\n"
        "\n"
        "https://fake.canva.com/2 10"
    )
    batch_file.write_text(batch_content, encoding='utf-8')
    
    # Mockujemy uruchomienie engine'u, aby nie wywoływał przeglądarki
    with patch('scraper.cli.CanvaScraperEngine') as mock_engine, \
         patch('scraper.cli.asyncio.run') as mock_asyncio_run:
         
        process_batch(str(batch_file), concurrent=2, debug=True)
        
        # Asercje (Sprawdzenia biznesowe)
        assert mock_engine.call_count == 2, "Powinien utworzyć 2 instancje silnika dla 2 linków"
        assert mock_asyncio_run.call_count == 2, "Powinien odpalić event loop 2 razy"
        
        # Ponieważ pierwszy link znajduje się w DRUGIEJ linijce pliku (z czterech)
        # nasz program wyświetli: [ZADANIE 2/4]
        assert "ZADANIE 2/4" in caplog.text
        assert "out1.pdf" in caplog.text

def test_process_batch_missing_file(caplog):
    """Test sprawdza jak aplikacja reaguje na brak pliku."""
    process_batch("nieistniejacy_plik.txt", 1, False)
    assert "nie istnieje" in caplog.text