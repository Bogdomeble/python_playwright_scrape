

# Canva Scraper CLI

Profesjonalne narzędzie działające w wierszu poleceń do asynchronicznego pobierania slajdów z prezentacji Canva i łączenia ich w pliki PDF. Wykorzystuje technologię Playwright.

## Nowości w najnowszej wersji 🚀
* **Autodetekcja końca prezentacji** – nie musisz już podawać liczby slajdów! Skrypt samodzielnie rozpozna (za pomocą porównywania obrazu i URL), kiedy dotarł do końca.
* **Tryb wsadowy (Batch)** – pobieraj dziesiątki prezentacji z pliku tekstowego za pomocą jednej komendy.
* **Automatyczne nazewnictwo** – jeśli nie podasz nazwy pliku, program wygeneruje bezpieczną nazwę z datą i godziną (np. `prezentacja_20260725_153000.pdf`).

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

## Użycie (Use Cases)

Główna składnia obsługuje teraz dwa tryby pracy (pojedynczy `--url` lub z pliku `--batch`):

```powershell
python main.py --url <ADRES_URL> [OPCJE]
# lub
python main.py --batch <PLIK_TXT> [OPCJE]
```

### Przypadek 1: Szybkie pobieranie (Pełna automatyka)
Narzędzie samo przeanalizuje ile slajdów ma prezentacja i utworzy plik z datą i godziną.
```powershell
python main.py --url "https://www.canva.com/design/XXXX/view?embed"
```

### Przypadek 2: Pełna kontrola (własna nazwa, własna ilość slajdów i limit obciążenia)
Użyj flag, jeśli chcesz sztywno wymusić ilość slajdów, nazwę pliku i pobierać max 2 zakładki na raz (dla wolniejszego łącza).
```powershell
python main.py --url "https://www.canva.com/design/XXXX/view?embed" -s 30 -o "szkolenie_2024.pdf" -c 2
```

### Przypadek 3: Pobieranie masowe z pliku (Tryb Batch)
Stwórz plik tekstowy (np. `postery.txt`), w którym wkleisz same linki (każdy w nowej linii). Możesz też obok linku dopisać po spacji nazwę pliku, np. `https://canva.link... moj_plik.pdf`.
```powershell
python main.py --batch postery.txt
```

### Przypadek 4: Tryb deweloperski (Debugowanie)
Zobaczysz na żywo w konsoli wszystkie informacje z silnika (jakie zakładki są otwierane, proces zgadywania slajdów itp.).
```powershell
python main.py --url "https://www.canva.com/design/XXXX/view?embed" --debug
```

## Budowanie aplikacji binarnej (.exe)

Możesz skompilować aplikację przy użyciu PyInstaller, by działała bez Pythona na innych komputerach:

```powershell
pip install pyinstaller
pyinstaller --clean  --noconfirm --onedir --name "CanvaScraper" --collect-all playwright main.py 
```