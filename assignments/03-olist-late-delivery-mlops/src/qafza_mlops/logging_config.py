"""Structured application logging to console and rotating file."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from src.qafza_mlops.config import Settings


def configure_logging(settings: Settings) -> None:
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
