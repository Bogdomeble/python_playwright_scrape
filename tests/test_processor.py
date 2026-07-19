import pytest
from PIL import Image
import io
import os
from scraper.processor import ImageProcessor

def test_process_screenshot():
    """Test sprawdza czy obraz z bajtów jest poprawnie ładowany i przycinany."""
    # Tworzymy fałszywy obrazek (czerwony kwadrat) w pamięci
    img = Image.new('RGB', (1920, 1080), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    fake_bytes = img_byte_arr.getvalue()

    # Wywołujemy naszą metodę
    processed_img = ImageProcessor.process_screenshot(fake_bytes, 1920, 1080)
    
    # Asserty sprawdzają warunki, jeśli fałsz -> test fail
    assert processed_img.size == (1920, 1080)
    assert processed_img.mode == 'RGB'

def test_create_pdf(tmp_path):
    """Test sprawdza czy plik PDF fizycznie się tworzy na dysku."""
    img1 = Image.new('RGB', (100, 100), color='blue')
    img2 = Image.new('RGB', (100, 100), color='green')
    
    # Używamy tmp_path (wbudowany ficzer pytesta) do zapisu w tymczasowym katalogu
    pdf_path = tmp_path / "test_output.pdf"
    
    ImageProcessor.create_pdf([img1, img2], str(pdf_path))
    
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0