import os
import io
from PIL import Image
from scraper.processor import ImageProcessor

def test_process_screenshot_standard():
    img_byte_arr = io.BytesIO()
    Image.new('RGB', (1920, 1080), color='red').save(img_byte_arr, format='PNG')
    
    processed = ImageProcessor.process_screenshot(img_byte_arr.getvalue(), 1920, 1080)
    assert processed.size == (1920, 1080)

def test_process_screenshot_with_crop():
    """Testuje tzw. Edge Case - czy dolny pasek (np. 65px) jest ucinany prawidłowo."""
    img_byte_arr = io.BytesIO()
    Image.new('RGB', (1920, 1080), color='blue').save(img_byte_arr, format='PNG')
    
    processed = ImageProcessor.process_screenshot(img_byte_arr.getvalue(), 1920, 1080, crop_bottom=65)
    assert processed.size == (1920, 1015) # 1080 minus 65px

def test_create_pdf_empty_list(caplog):
    """Sprawdza bezpieczne zakończenie działania, jeśli sieć zawiodła i nie ma obrazów."""
    ImageProcessor.create_pdf([], "dummy.pdf")
    # Zamiast błędu aplikacji (Crash), powinien być tylko log ostrzegawczy
    assert "Brak obrazów do zapisania" in caplog.text

def test_create_pdf_success(tmp_path):
    img1 = Image.new('RGB', (100, 100), color='blue')
    pdf_path = tmp_path / "out.pdf"
    
    ImageProcessor.create_pdf([img1], str(pdf_path))
    assert os.path.exists(pdf_path)