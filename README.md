
# Canva Scraper CLI

Profesjonalne narzędzie działające w wierszu poleceń do asynchronicznego pobierania slajdów z prezentacji Canva i łączenia ich w pliki PDF. Wykorzystuje technologię Playwright.

## Wymagania

- Python 3.9+
- Przeglądarka Google Chrome zainstalowana w systemie.

## Instalacja
1. Pobierz repozytorium.
2. Zainstaluj zależności:

```powershell
pip install -r requirements.txt
playwright install chrome
```

Użycie (Use Cases)

Główna składnia:

```powershell
python main.py <URL> -s <LICZBA_SLAJDÓW> [OPCJE]
```

### Przypadek 1: Standardowe pobieranie


python main.py "https://www.canva.com/design/XXXX/view?embed" -s 30

(Zapisze plik pod domyślną nazwą prezentacja.pdf)

### Przypadek 2: Własna nazwa pliku i mniejsze obciążenie sieci


```powershell
python main.py "https://www.canva.com/design/XXXX/view?embed" -s 30 -o "szkolenie_2024.pdf" -c 2
```

(-c 2 oznacza max 2 karty pobierane jednocześnie)

### Przypadek 3: Tryb deweloperski (Debugowanie)


```powershell
python main.py "URL" -s 5 --debug
```
Budowanie aplikacji binarnej (.exe)

Możesz skompilować aplikację przy użyciu PyInstaller:

```powershell
pip install pyinstaller
pyinstaller --clean --onedir --name "CanvaScraper" --collect-all playwright main.py
```
