# main.py
import sys
import traceback

if __name__ == "__main__":
    try:
        from scraper.cli import main_cli
        main_cli()
        
    except SystemExit as e:
        # Pozwalamy na naturalne zamykanie (np. przez poprawne zakończenie lub argparse)
        sys.exit(e.code if hasattr(e, 'code') and e.code is not None else 0)
        
    except KeyboardInterrupt:
        # Złapanie Ctrl+C bez wyświetlania brzydkich błędów systemowych
        print("\n[STOP] Program przerwany przez uzytkownika.")
        sys.exit(0)
        
    except Exception as e:
        # Gdy coś wybuchnie, wielki czerwony alarm, który nie pozwoli oknu zniknąć!
        print("\n" + "!"*60)
        print("KRYTYCZNY BLAD APLIKACJI - COS POSZLO NIE TAK")
        print("!"*60 + "\n")
        
        # Wypisuje dokładne miejsce, gdzie kod się popsuł
        traceback.print_exc()
        
        print("\n" + "!"*60)
        input("Nacisnij ENTER, aby zamknac okno...")
        sys.exit(1)