# main.py
import sys
import os
import traceback
import signal
import logging  # <--- Dodany import do obsługi logów

_is_shutting_down = False

def handle_sigint(sig, frame):
    """Twarde ubicie procesu z bezpiecznym zapisem logów i wyciszeniem błędów."""
    global _is_shutting_down
    if not _is_shutting_down:
        _is_shutting_down = True
        print("\n[STOP] Program przerwany przez uzytkownika (Ctrl+C). Natychmiastowe zamykanie...")
        
        # 1. Zabezpieczenie logów: Wymuszamy zrzucenie całej pamięci podręcznej logów do plików na dysku!
        logging.shutdown()
        
        # 2. Magiczna sztuczka z wyciszeniem błędów rury (pipe) z konsoli
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            os.dup2(devnull, sys.stderr.fileno())
        except Exception:
            pass
            
        # 3. Odcięcie zasilania
        os._exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    
    try:
        from scraper.cli import main_cli
        main_cli()
        
    except SystemExit as e:
        sys.exit(e.code if hasattr(e, 'code') and e.code is not None else 0)
        
    except Exception as e:
        print("\n" + "!"*60)
        print("KRYTYCZNY BLAD APLIKACJI - COS POSZLO NIE TAK")
        print("!"*60 + "\n")
        traceback.print_exc()
        print("\n" + "!"*60)
        input("Nacisnij ENTER, aby zamknac okno...")
        sys.exit(1)