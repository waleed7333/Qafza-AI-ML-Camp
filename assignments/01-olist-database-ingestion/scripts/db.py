"""Shared, small database/configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ASSIGNMENT_DIR = Path(__file__).resolve().parents[1]


def load_environment() -> None:
    load_dotenv(ASSIGNMENT_DIR / ".env")


def connect() -> psycopg.Connection:
    load_environment()
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB", "olist"),
        user=os.getenv("POSTGRES_USER", "olist"),
        password=os.getenv("POSTGRES_PASSWORD", "olist_dev_password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
