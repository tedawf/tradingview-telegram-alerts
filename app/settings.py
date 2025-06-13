import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / "settings.json"


class Settings:
    def __init__(self):
        self.file = SETTINGS_FILE
        if not self.file.exists():
            self.reset_defaults()
        self.load()

    def reset_defaults(self):
        self.data = {
            "default_interval": "1",
            "chart_theme": "light",
            "symbol_map": {
                # "BTCUSD": "COINBASE",
            },
        }
        self.save()

    def load(self):
        with open(self.file, "r") as f:
            self.data = json.load(f)

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def get_symbol(self, ticker):
        return self.data["symbol_map"].get(ticker.upper())

    def set_symbol(self, ticker, exchange):
        self.data["symbol_map"][ticker.upper()] = f"{exchange.upper()}:{ticker}"
        self.save()

    def remove_symbol(self, ticker):
        ticker = ticker.upper()
        if ticker in self.data["symbol_map"]:
            del self.data["symbol_map"][ticker]
            self.save()
            return True
        return False


settings = Settings()
