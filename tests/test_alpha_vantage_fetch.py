import csv
import json
import tempfile
import unittest
from pathlib import Path

import alpha_vantage_fetch as av


class TestExtractRows(unittest.TestCase):
    def test_extract_rows_returns_sorted_rows(self):
        payload = {
            "Time Series (5min)": {
                "2026-04-22 10:05:00": {
                    "1. open": "102.00",
                    "2. high": "103.00",
                    "3. low": "101.50",
                    "4. close": "102.80",
                    "5. volume": "1200",
                },
                "2026-04-22 10:00:00": {
                    "1. open": "100.00",
                    "2. high": "101.20",
                    "3. low": "99.80",
                    "4. close": "100.90",
                    "5. volume": "1000",
                },
            }
        }

        rows = av.extract_rows(payload, symbol="IBM", interval="5min")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["timestamp"], "2026-04-22 10:00:00")
        self.assertEqual(rows[1]["timestamp"], "2026-04-22 10:05:00")
        self.assertEqual(rows[0]["symbol"], "IBM")
        self.assertEqual(rows[0]["close"], "100.90")

    def test_extract_rows_raises_when_api_returns_information(self):
        payload = {"Information": "API rate limit reached"}

        with self.assertRaises(RuntimeError) as ctx:
            av.extract_rows(payload, symbol="IBM", interval="5min")

        self.assertIn("rate limit", str(ctx.exception).lower())


class TestExportWriters(unittest.TestCase):
    def test_write_csv_and_json_outputs_files(self):
        rows = [
            {
                "symbol": "IBM",
                "interval": "5min",
                "timestamp": "2026-04-22 10:00:00",
                "open": "100.00",
                "high": "101.20",
                "low": "99.80",
                "close": "100.90",
                "volume": "1000",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "out.csv"
            json_path = tmp_path / "out.json"

            av.write_csv(rows, str(csv_path))
            av.write_json(rows, str(json_path))

            self.assertTrue(csv_path.exists())
            self.assertTrue(json_path.exists())

            with csv_path.open("r", encoding="utf-8", newline="") as f:
                csv_rows = list(csv.DictReader(f))
            self.assertEqual(len(csv_rows), 1)
            self.assertEqual(csv_rows[0]["symbol"], "IBM")

            with json_path.open("r", encoding="utf-8") as f:
                json_rows = json.load(f)
            self.assertEqual(len(json_rows), 1)
            self.assertEqual(json_rows[0]["symbol"], "IBM")


if __name__ == "__main__":
    unittest.main()
