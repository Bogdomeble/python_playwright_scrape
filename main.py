# main.py
import sys
from scraper.cli import main_cli

if __name__ == "__main__":
    try:
        main_cli()
    except (KeyboardInterrupt, SystemExit):
        # Wyciszenie błędów przy ręcznym zamykaniu (Ctrl+C lub "X" w konsoli)
        sys.exit(0)
    except Exception:
        sys.exit(1)