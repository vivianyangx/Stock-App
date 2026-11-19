"""Refresh the point-in-time price history used by Professional ML v1.

Yahoo is used only for the research prototype.  A licensed SIP/OPRA provider
should replace this downloader before the model is represented as production
market infrastructure or redistributed publicly.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "ml_results" / "ml_price_cache.pkl"
TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO",
    "JPM", "XOM", "UNH", "JNJ", "PG", "COST", "HD", "AMD", "NFLX",
    "SPY", "QQQ", "IWM", "DIA", "XLK", "XLC", "XLY", "XLP", "XLF",
    "XLE", "XLV", "XLI", "XLB", "XLRE", "XLU", "TQQQ",
]


def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)
    frames: dict[str, pd.DataFrame] = {}
    failures: list[str] = []
    for ticker in TICKERS:
        try:
            frame = yf.download(
                ticker, period="10y", interval="1d", auto_adjust=True,
                actions=False, progress=False, repair=True, threads=False,
                timeout=30,
            )
            if isinstance(frame.columns, pd.MultiIndex):
                frame.columns = frame.columns.get_level_values(0)
            frame = frame[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
            if len(frame) < 1_000:
                raise ValueError(f"only {len(frame)} observations")
            frame.index = pd.DatetimeIndex(frame.index).tz_localize(None).normalize()
            frames[ticker] = frame
            print(f"{ticker:>5}: {frame.index.min().date()} → {frame.index.max().date()} · {len(frame):,}")
        except Exception as exc:
            failures.append(f"{ticker}: {exc}")
    if failures:
        raise RuntimeError("History refresh failed:\n" + "\n".join(failures))
    pd.to_pickle(frames, OUTPUT)
    print(f"Wrote {OUTPUT} with {len(frames)} symbols")


if __name__ == "__main__":
    main()

