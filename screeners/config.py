import os

import yaml


class BaseConfig:
    def __init__(self, values: dict):
        self._values = values

    def __getitem__(self, key):
        return self._values[key]


class ConfigScraper(BaseConfig):
    def __init__(self, values: dict):
        super().__init__(values)

        self.sleep_after_click: int = int(values["sleep_after_click"])
        self.retry_times: int = int(values["retry_times"])
        self.min_current_ratio: float = float(values["min_current_ratio"])
        self.min_trading_days: int = int(values["min_trading_days"])


class ConfigGiga(BaseConfig):
    def __init__(self, values: dict):
        super().__init__(values)

        self.name: str = values["name"]
        self.url: str = values["url"]
        self.target: str = os.path.join(os.getcwd(), values["target"])


class ConfigIgnoredTickers(BaseConfig):
    def __init__(self, values: dict):
        super().__init__(values)

        self.target: str = os.path.join(os.getcwd(), values["target"])


class ConfigRevive(BaseConfig):
    def __init__(self, values: dict):
        super().__init__(values)

        self.sleep: float = float(values["sleep"])
        self.limit: int = int(values["limit"])
        self.ignore_after_days: int = int(values["ignore_after_days"])


class Config(BaseConfig):
    def __init__(self, values: dict):
        super().__init__(values)

        self.scraper = ConfigScraper(values["scraper"])
        self.giga = [ConfigGiga(_) for _ in values["giga"]]
        self.revive = ConfigRevive(values["revive"])
        self.ignored_tickers = ConfigIgnoredTickers(values["ignored_tickers"])

    def __getitem__(self, key: str):
        return self._values[key]


with open("config.yml", "r") as file:
    config: Config = Config(yaml.safe_load(file))
