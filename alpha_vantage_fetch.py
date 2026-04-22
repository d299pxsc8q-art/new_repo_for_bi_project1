#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://www.alphavantage.co/query"


def fetch_intraday(symbol: str, interval: str, api_key: str, outputsize: str) -> dict:
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    url = f"{API_BASE}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "accept": "application/json",
            "user-agent": "alpha-vantage-fetch-script/1.0",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except HTTPError as err:
        raise RuntimeError(f"Erreur HTTP {err.code}: {err.reason}") from err
    except URLError as err:
        raise RuntimeError(f"Erreur réseau: {err.reason}") from err
    except json.JSONDecodeError as err:
        raise RuntimeError("Réponse JSON invalide depuis Alpha Vantage.") from err


def extract_rows(data: dict, symbol: str, interval: str) -> list[dict]:
    note = data.get("Note")
    information = data.get("Information")
    error_message = data.get("Error Message")
    if note:
        raise RuntimeError(note)
    if information:
        raise RuntimeError(information)
    if error_message:
        raise RuntimeError(error_message)

    key = f"Time Series ({interval})"
    series = data.get(key)
    if not isinstance(series, dict) or not series:
        raise RuntimeError("Aucune série temporelle trouvée dans la réponse.")
    rows = []
    for timestamp in sorted(series.keys()):
        candle = series[timestamp]
        rows.append(
            {
                "symbol": symbol,
                "interval": interval,
                "timestamp": timestamp,
                "open": candle.get("1. open"),
                "high": candle.get("2. high"),
                "low": candle.get("3. low"),
                "close": candle.get("4. close"),
                "volume": candle.get("5. volume"),
            }
        )
    return rows


def write_csv(rows: list[dict], output_path: str) -> None:
    fieldnames = ["symbol", "interval", "timestamp", "open", "high", "low", "close", "volume"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: list[dict], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def resolve_api_key(cli_api_key: str | None, api_key_file: str | None) -> str | None:
    if cli_api_key and cli_api_key.strip():
        return cli_api_key.strip()

    for env_var in ("ALPHA_VANTAGE_API_KEY", "AV_API_KEY"):
        value = os.getenv(env_var)
        if value and value.strip():
            return value.strip()

    if api_key_file:
        key_path = Path(api_key_file).expanduser()
        if key_path.exists():
            key_value = key_path.read_text(encoding="utf-8").strip()
            if key_value:
                return key_value

    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Récupère les données intraday depuis Alpha Vantage."
    )
    parser.add_argument(
        "--api-key",
        help="Clé API Alpha Vantage (optionnelle si ALPHA_VANTAGE_API_KEY est définie).",
    )
    parser.add_argument(
        "--api-key-file",
        default="alpha_vantage_api_key.txt",
        help="Fichier contenant la clé API sur la première ligne (utile pour Power BI).",
    )
    parser.add_argument("--symbol", default="IBM", help="Symbole boursier (ex: IBM, AAPL).")
    parser.add_argument(
        "--interval",
        default="5min",
        choices=["1min", "5min", "15min", "30min", "60min"],
        help="Intervalle des données intraday.",
    )
    parser.add_argument(
        "--outputsize",
        default="compact",
        choices=["compact", "full"],
        help="Quantité de données retournées.",
    )
    parser.add_argument(
        "--format",
        default="csv",
        choices=["csv", "json"],
        help="Format de sortie pour Power BI.",
    )
    parser.add_argument(
        "--output-file",
        default="alpha_vantage_intraday.csv",
        help="Chemin du fichier exporté.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    api_key = resolve_api_key(args.api_key, args.api_key_file)

    if not api_key:
        print(
            "Échec: fournissez --api-key, définissez ALPHA_VANTAGE_API_KEY, ou créez alpha_vantage_api_key.txt.",
            file=sys.stderr,
        )
        return 1

    try:
        data = fetch_intraday(
            symbol=args.symbol,
            interval=args.interval,
            api_key=api_key,
            outputsize=args.outputsize,
        )
        rows = extract_rows(data, symbol=args.symbol, interval=args.interval)
        if args.format == "csv":
            write_csv(rows, args.output_file)
        else:
            write_json(rows, args.output_file)
        print(f"Fichier généré: {args.output_file} ({len(rows)} lignes)")
    except RuntimeError as err:
        print(f"Échec: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
