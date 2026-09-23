"""
Stock Intelligence Platform
Professional-grade stock analysis web app built with Streamlit
"""

import warnings
warnings.filterwarnings('ignore')

import html
import io
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Investor Research",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark background */
.stApp { background-color: #0a0e1a; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0d1321;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d1321 0%, #111827 100%);
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: left;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #334155; }
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.metric-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 6px;
}

/* Verdict banner */
.verdict-banner {
    border-radius: 12px;
    padding: 22px 32px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin: 16px 0;
    border: 1px solid;
}
.verdict-buy  { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.3); }
.verdict-sell { background: rgba(239,68,68,0.08);  border-color: rgba(239,68,68,0.3); }
.verdict-hold { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.3); }
.verdict-wait { background: rgba(100,116,139,0.08);border-color: rgba(100,116,139,0.3);}

.verdict-score {
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
}
.verdict-title {
    font-size: 20px;
    font-weight: 700;
    color: #f1f5f9;
}
.verdict-desc { font-size: 13px; color: #94a3b8; margin-top: 4px; }

/* Signal pills */
.signal-pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.pill-buy  { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.pill-sell { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.pill-wait { background: rgba(100,116,139,0.15);color: #94a3b8; border: 1px solid rgba(100,116,139,0.3);}

/* Section header */
.section-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #475569;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2d45;
}

/* News item */
.news-item {
    background: #0d1321;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.news-title { font-size: 13px; color: #cbd5e1; line-height: 1.5; }
.news-meta  { font-size: 11px; color: #475569; margin-top: 4px; }

/* Trading plan */
.plan-card {
    background: linear-gradient(145deg, #0d1321 0%, #111827 100%);
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 20px;
    min-height: 138px;
}
.plan-kicker {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}
.plan-price { color: #f8fafc; font-size: 25px; font-weight: 750; margin: 8px 0 5px; }
.plan-copy { color: #94a3b8; font-size: 12px; line-height: 1.55; }
.factor-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(30,45,69,.72);
    color: #94a3b8;
    font-size: 12px;
}
.factor-row:last-child { border-bottom: 0; }
.factor-value { color: #e2e8f0; font-weight: 600; text-align: right; }
.disclaimer {
    background: rgba(59,130,246,.06);
    border: 1px solid rgba(59,130,246,.18);
    border-radius: 10px;
    color: #64748b;
    font-size: 11px;
    line-height: 1.65;
    padding: 13px 16px;
}
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0 30px;
}
.brand-lockup { display: flex; align-items: center; gap: 14px; }
.brand-mark {
    width: 44px; height: 44px; border-radius: 13px;
    display: grid; place-items: center;
    background: linear-gradient(145deg, #7ce7d1, #44cdb4);
    color: #07131c; font-size: 18px; font-weight: 800;
    box-shadow: 0 10px 28px rgba(68,205,180,.16);
}
.brand-name { color: #f8fafc; font-size: 17px; font-weight: 750; }
.brand-line { color: #64748b; font-size: 11px; margin-top: 3px; }
.data-badge {
    border: 1px solid rgba(94,234,212,.28);
    border-radius: 999px; padding: 7px 12px;
    color: #5eead4; font-size: 10px; font-weight: 750;
    letter-spacing: 1.2px;
}
.data-dot { color: #5eead4; margin-right: 6px; }

/* Streamlit controls */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: #0d1321;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    color: #94a3b8;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] { color: #f8fafc !important; border-color: #3b82f6 !important; }

@media (max-width: 900px) {
    .metric-value { font-size: 20px; }
    .verdict-banner { padding: 18px; gap: 12px; }
    .verdict-score { font-size: 34px; }
}

/* Reduce Streamlit branding while preserving the mobile sidebar control */
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.block-container { padding-top: 24px; }

/* Mobile investing app shell */
.stApp {
    background:
        radial-gradient(circle at 18% 12%, rgba(125,93,236,.10), transparent 28%),
        radial-gradient(circle at 82% 78%, rgba(173,219,54,.10), transparent 25%),
        #e9ebe2;
    color: #171522;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.block-container {
    max-width: 480px !important;
    margin: 24px auto 48px;
    padding: 20px 18px 30px !important;
    background: #fbfbf8;
    border: 1px solid rgba(70,57,108,.10);
    border-radius: 34px;
    box-shadow: 0 30px 80px rgba(48,42,68,.16);
}
.mobile-nav {
    display:flex; align-items:center; justify-content:space-between;
    margin:2px 2px 18px; padding:11px 12px;
    background:rgba(255,255,255,.82); border:1px solid #e7e3ef;
    border-radius:18px; box-shadow:0 8px 24px rgba(67,55,101,.07);
}
.ticker-identity { display:flex; align-items:center; gap:10px; min-width:0; }
.ticker-monogram {
    width:38px; height:38px; border-radius:12px; flex:0 0 auto;
    display:grid; place-items:center; color:white; font-size:12px; font-weight:850;
    background:linear-gradient(145deg,#7651e8,#9575ef);
    box-shadow:0 8px 18px rgba(111,74,232,.24);
}
.ticker-lockup { text-align:left; min-width:0; }
.ticker-name { font-size:15px; color:#171522; font-weight:850; letter-spacing:.25px; }
.ticker-company { font-size:10px; color:#8a8498; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:210px; }
.market-pill {
    display:flex; align-items:center; gap:6px; flex:0 0 auto;
    padding:7px 9px; border-radius:999px; background:#f2f8df;
    border:1px solid #dcebb3; color:#617b19;
    font-size:8px; font-weight:800; letter-spacing:.7px;
}
.market-dot { width:6px; height:6px; border-radius:50%; background:#95c824; box-shadow:0 0 0 3px rgba(149,200,36,.14); }
.price-panel {
    background:linear-gradient(145deg,#f1edff 0%,#f7f6fb 58%,#f4f8e9 100%);
    border:1px solid #e6e0f5; border-radius:20px; padding:17px 17px; margin-bottom:10px;
    box-shadow:0 10px 28px rgba(89,66,145,.07);
}
.eyebrow { color:#827b90; font-size:9px; font-weight:750; text-transform:uppercase; letter-spacing:.85px; }
.hero-price { color:#11121a; font-size:32px; font-weight:800; letter-spacing:-1.4px; margin:3px 0 2px; }
.positive { color:#6c00f5; font-weight:700; }
.negative { color:#ef6170; font-weight:700; }
.mini-copy { color:#85858e; font-size:10px; }
.stat-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; margin:8px 0 12px; }
.stat-cell { background:#fff; border:1px solid #e9e6ef; border-radius:14px; padding:11px 12px; min-height:58px; box-shadow:0 5px 16px rgba(62,53,82,.04); }
.stat-label { color:#8b8b93; font-size:9px; margin-bottom:5px; }
.stat-value { color:#171821; font-size:13px; font-weight:750; }
.dark-chart-title { color:#f6f6fa; font-size:12px; font-weight:700; }
.plan-strip { display:grid; grid-template-columns:1fr 1fr; gap:7px; margin:8px 0; }
.mobile-card { background:#fff; border:1px solid #e8e4ef; border-radius:16px; padding:13px 14px; box-shadow:0 6px 18px rgba(62,53,82,.045); }
.mobile-card .value { color:#161720; font-size:18px; font-weight:800; margin-top:5px; }
.mobile-card .value.lime { color:#84ad19; }
.mobile-card .value.purple { color:#7045df; }
.mobile-card .value.red { color:#ef6170; }
.detail-card { background:#fff; border:1px solid #e8e4ef; border-radius:16px; padding:6px 14px; margin:8px 0; box-shadow:0 6px 18px rgba(62,53,82,.04); }
.detail-row { display:flex; justify-content:space-between; align-items:center; padding:11px 0; border-bottom:1px solid #d9d9df; font-size:11px; color:#777780; }
.detail-row:last-child { border-bottom:0; }
.detail-row b { color:#171821; font-weight:650; text-align:right; }
.mobile-note { color:#85808f; font-size:10px; line-height:1.55; padding:8px 3px; }
.stTabs [data-baseweb="tab-list"] { background:#efedf3; padding:4px; border-radius:14px; gap:3px; box-shadow:inset 0 0 0 1px rgba(88,73,120,.05); overflow-x:auto; flex-wrap:nowrap; scrollbar-width:none; }
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display:none; }
.stTabs [data-baseweb="tab"] { background:transparent; border:0; color:#777181; border-radius:10px; padding:8px 14px; flex:0 0 auto; font-weight:650; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#7148e3,#8a67eb) !important; color:white !important; border:0 !important; box-shadow:0 5px 13px rgba(113,72,227,.23); }
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }
div[data-testid="stButton"] button { border-radius:999px; min-height:45px; font-weight:750; border:0; }
div[data-testid="stButton"] button[kind="primary"] { background:#c8f51d; color:#11121a; }
div[data-testid="stButton"] button[kind="secondary"] { background:#6c00f5; color:white; }
div[data-testid="stExpander"] { background:rgba(255,255,255,.86); border:1px solid #e5e1ec; border-radius:16px; overflow:hidden; box-shadow:0 6px 20px rgba(62,53,82,.04); }
div[data-testid="stMetric"] { background:#ececef; border-radius:13px; padding:10px; }
label, .stMarkdown, [data-testid="stCaptionContainer"] { color:#34343d; }

@media (max-width: 560px) {
    .stApp { background:#f8f8f5; }
    .block-container { margin:0; border:0; border-radius:0; box-shadow:none; max-width:100% !important; min-height:100vh; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────
def fetch_nasdaq(ticker: str, period: str) -> pd.DataFrame:
    """Keyless Nasdaq fallback for daily US-listed stock and ETF history."""
    if not ticker.replace('-', '').isalnum() or '.' in ticker:
        raise ValueError('Nasdaq fallback currently supports plain US-listed symbols')
    years = {'1y': 1, '2y': 2, '5y': 5, '10y': 10}.get(period, 5)
    end = pd.Timestamp.now().normalize()
    start = end - pd.DateOffset(years=years, days=10)
    rows = []
    matched_asset_class = None
    for asset_class in ('stocks', 'etf'):
        params = urlencode({
            'assetclass': asset_class,
            'fromdate': start.strftime('%Y-%m-%d'),
            'todate': end.strftime('%Y-%m-%d'),
            'limit': 5000,
        })
        request = Request(
            f'https://api.nasdaq.com/api/quote/{ticker}/historical?{params}',
            headers={
                'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                               'AppleWebKit/537.36 Chrome/125.0 Safari/537.36'),
                'Accept': 'application/json,text/plain,*/*',
                'Referer': 'https://www.nasdaq.com/',
            },
        )
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
        rows = (((payload.get('data') or {}).get('tradesTable') or {}).get('rows') or [])
        if rows:
            matched_asset_class = asset_class
            break
    if not rows:
        raise ValueError(f'No Nasdaq price data returned for {ticker}')
    raw = pd.DataFrame(rows).rename(columns={
        'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume',
    })
    raw['Date'] = pd.to_datetime(raw['Date'], errors='coerce')
    for column in ['Open', 'High', 'Low', 'Close', 'Volume']:
        raw[column] = pd.to_numeric(
            raw[column].astype(str).str.replace(r'[$,]', '', regex=True),
            errors='coerce',
        )
    raw = raw.dropna(subset=['Date', 'Open', 'High', 'Low', 'Close'])
    raw = raw.set_index('Date').sort_index()
    raw['Volume'] = raw['Volume'].fillna(0)
    raw['Adj Close'] = raw['Close']
    label = 'ETF' if matched_asset_class == 'etf' else 'stock'
    raw.attrs['provider'] = f'Nasdaq fallback ({label})'
    return raw


def fetch_stooq(ticker: str, period: str) -> pd.DataFrame:
    """Fallback daily OHLCV source for US tickers when Yahoo is rate-limited."""
    if '.' in ticker:
        raise ValueError('Stooq fallback currently supports US symbols only')
    years = {'1y': 1, '2y': 2, '5y': 5, '10y': 10}.get(period, 5)
    end = pd.Timestamp.now().normalize()
    start = end - pd.DateOffset(years=years, days=10)
    params = urlencode({
        's': f'{ticker.lower()}.us', 'd1': start.strftime('%Y%m%d'),
        'd2': end.strftime('%Y%m%d'), 'i': 'd'
    })
    request = Request(
        f'https://stooq.com/q/d/l/?{params}',
        headers={'User-Agent': 'Mozilla/5.0 investor-research-tracker'}
    )
    with urlopen(request, timeout=20) as response:
        payload = response.read()
    raw = pd.read_csv(io.BytesIO(payload))
    if raw.empty or 'Date' not in raw.columns:
        raise ValueError(f'No Stooq price data returned for {ticker}')
    raw['Date'] = pd.to_datetime(raw['Date'], errors='coerce')
    raw = raw.dropna(subset=['Date']).set_index('Date').sort_index()
    raw['Adj Close'] = raw['Close']
    raw.attrs['provider'] = 'Stooq fallback'
    return raw


@st.cache_data(ttl=300)
def fetch_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    yahoo_error = None
    try:
        raw = yf.download(
            ticker, period=period, interval='1d', progress=False,
            auto_adjust=False, repair=True, keepna=False, threads=False,
            timeout=15
        )
        if raw.empty:
            raise ValueError(f"No Yahoo price data returned for {ticker}")
        raw.attrs['provider'] = 'Yahoo Finance'
    except Exception as exc:
        yahoo_error = exc
        try:
            raw = fetch_nasdaq(ticker, period)
        except Exception as nasdaq_error:
            try:
                raw = fetch_stooq(ticker, period)
            except Exception as stooq_error:
                raise RuntimeError(
                    f'All market-data providers failed. Yahoo: {yahoo_error}; '
                    f'Nasdaq: {nasdaq_error}; Stooq: {stooq_error}'
                ) from stooq_error

    provider = raw.attrs.get('provider', 'Unknown')
    df  = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df['Close'].astype(float)
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    df['MA20'] = close.rolling(20).mean()
    df['MA50'] = close.rolling(50).mean()
    df['MA200'] = close.rolling(200).mean()

    # Wilder RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD(12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands(20, 2) and Wilder ATR(14)
    rolling_std = close.rolling(20).std()
    df['BB_upper'] = df['MA20'] + rolling_std * 2
    df['BB_lower'] = df['MA20'] - rolling_std * 2
    prev_close = close.shift(1)
    true_range = pd.concat([
        high - low, (high - prev_close).abs(), (low - prev_close).abs()
    ], axis=1).max(axis=1)
    df['ATR'] = true_range.ewm(alpha=1 / 14, adjust=False).mean()
    df['Volume_MA20'] = df['Volume'].rolling(20).mean()
    # Use dividend-adjusted prices for historical return statistics when present.
    df['ReturnClose'] = (df['Adj Close'].astype(float)
                         if 'Adj Close' in df.columns else close)
    df.attrs['provider'] = provider
    return df


def finite(value, fallback=0.0) -> float:
    """Return a safe float for UI math when an indicator is missing."""
    try:
        value = float(value)
        return value if np.isfinite(value) else float(fallback)
    except (TypeError, ValueError):
        return float(fallback)


def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    source_attrs = df.attrs.copy()
    df = df.copy()
    df['Signal'] = 'HOLD'
    df['Score']  = 0
    for i in range(1, len(df)):
        sc = 0
        close, ma20, ma50 = df['Close'].iloc[i], df['MA20'].iloc[i], df['MA50'].iloc[i]
        rsi,  macd, macd_s = df['RSI'].iloc[i], df['MACD'].iloc[i], df['MACD_signal'].iloc[i]
        vol, vol_ma = df['Volume'].iloc[i], df['Volume_MA20'].iloc[i]
        bbl = df['BB_lower'].iloc[i]

        if close > ma20:           sc += 15
        if ma20  > ma50:           sc += 15
        if close > df['MA200'].iloc[i]: sc += 10
        if 40 < rsi < 65:          sc += 20
        if macd > macd_s:          sc += 15
        if close <= bbl * 1.02:    sc += 10
        if vol   > vol_ma * 1.3:   sc += 15
        if rsi   > 75:             sc -= 25
        if close < ma20:           sc -= 20
        if macd  < 0:              sc -= 10

        df.iloc[i, df.columns.get_loc('Score')]  = sc
        df.iloc[i, df.columns.get_loc('Signal')] = (
            'BUY' if sc >= 60 else 'SELL' if sc <= 20 else 'HOLD'
        )
    df.attrs.update(source_attrs)
    return df


def build_trade_plan(df: pd.DataFrame, account_size: float, risk_pct: float,
                     horizon: str) -> dict:
    """Create a compact support/risk/resistance map; outputs are not orders."""
    last = df.iloc[-1]
    cur = finite(last['Close'])
    atr = max(finite(last['ATR'], cur * 0.02), cur * 0.005)
    recent = df.tail(60)
    support_20 = finite(recent['Low'].tail(20).min(), cur - atr)
    support_60 = finite(recent['Low'].tail(60).min(), support_20)
    resistance_20 = finite(recent['High'].tail(20).max(), cur + atr)
    resistance_60 = finite(recent['High'].tail(60).max(), resistance_20)
    ma20 = finite(last['MA20'], cur)

    stop_buffer = {'Tactical (1–10 days)': .25,
                   'Swing (2–8 weeks)': .50,
                   'Position (2–12 months)': 1.00}[horizon]
    support_anchor = max(support_20, ma20)
    entry_high = min(cur, support_anchor + atr * .35)
    entry_low = min(entry_high, max(0.01, support_anchor - atr * .35))
    stop = max(0.01, support_20 - atr * stop_buffer)
    risk_per_share = max(cur - stop, atr * .5)
    target_1 = max(resistance_20, cur + atr * .50)
    target_2 = max(resistance_60, target_1 + atr * .75)
    risk_budget = max(0.0, account_size * risk_pct / 100)
    shares = int(risk_budget // risk_per_share) if risk_per_share > 0 else 0
    max_affordable = int(account_size // entry_high) if entry_high > 0 else 0
    shares = min(shares, max_affordable)
    return {
        'entry_low': entry_low, 'entry_high': entry_high, 'stop': stop,
        'target_1': target_1, 'target_2': target_2,
        'risk_per_share': risk_per_share, 'risk_budget': risk_budget,
        'shares': shares, 'position_value': shares * entry_high,
        'rr1': (target_1 - entry_high) / risk_per_share,
        'rr2': (target_2 - entry_high) / risk_per_share,
        'support': support_20, 'support_60': support_60,
        'resistance': resistance_20, 'resistance_60': resistance_60,
    }


@st.cache_data(ttl=600)
def get_sentiment(ticker: str) -> tuple:
    try:
        news = yf.Ticker(ticker).news
        scores, items = [], []
        for a in news[:15]:
            c = a.get('content', {})
            t = c.get('title', '') if isinstance(c, dict) else ''
            if t:
                p = TextBlob(t).sentiment.polarity
                scores.append(p)
                items.append({'title': t, 'polarity': p})
        avg = sum(scores) / len(scores) if scores else 0
        return avg, items
    except:
        return 0, []


def score_summary(sig, chg, sent, atr_pct) -> tuple:
    sc = 50
    if sig == 'BUY':   sc += 20
    elif sig == 'SELL': sc -= 20
    if chg > 3:  sc += 15
    elif chg < -3: sc -= 15
    if sent > 0.1:  sc += 10
    elif sent < -0.1: sc -= 10
    if atr_pct > 5: sc -= 5
    sc = max(0, min(100, sc))
    if   sc >= 75: verdict, css = 'Conviction setup', 'buy'
    elif sc >= 60: verdict, css = 'Constructive', 'buy'
    elif sc <= 30: verdict, css = 'Defensive', 'sell'
    elif sc <= 45: verdict, css = 'Fragile', 'sell'
    else:          verdict, css = 'Neutral', 'wait'
    return sc, verdict, css


# ── Plotly chart ──────────────────────────────────────────────
def build_mobile_chart(df: pd.DataFrame, window: str) -> go.Figure:
    """A single, correctly scaled price chart designed for a phone viewport."""
    sessions = {'1M': 22, '3M': 66, '6M': 132, '1Y': 252}[window]
    view = df.tail(sessions).copy()
    up = '#c8f51d'
    down = '#6c00f5'

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=view.index,
        open=view['Open'], high=view['High'], low=view['Low'], close=view['Close'],
        name='Price',
        increasing_line_color=up, increasing_fillcolor=up,
        decreasing_line_color=down, decreasing_fillcolor=down,
        whiskerwidth=.35,
        hovertemplate=(
            '%{x|%b %d, %Y}<br>Open $%{open:.2f}<br>High $%{high:.2f}'
            '<br>Low $%{low:.2f}<br>Close $%{close:.2f}<extra></extra>'
        )
    ))
    fig.add_trace(go.Scatter(
        x=view.index, y=view['MA20'], name='20D avg',
        line=dict(color='#9b76ff', width=1.35),
        hovertemplate='20D avg $%{y:.2f}<extra></extra>'
    ))

    last = finite(view['Close'].iloc[-1])
    fig.add_hline(
        y=last, line_width=1, line_dash='dot', line_color='rgba(200,245,29,.45)',
        annotation_text=f' ${last:.2f} ', annotation_position='right',
        annotation_font_color='#11121a', annotation_bgcolor=up,
        annotation_font_size=10
    )
    fig.update_layout(
        height=315,
        paper_bgcolor='#161621', plot_bgcolor='#161621',
        font=dict(family='Inter', color='#9a9aa5', size=10),
        margin=dict(l=8, r=8, t=38, b=8),
        title=dict(text=f'Price · {window}', x=.04, y=.96,
                   font=dict(color='#f8f8fb', size=12)),
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#f7f7f3', bordercolor='#e4e4e8',
                        font=dict(color='#161621', size=11)),
        legend=dict(orientation='h', x=.98, xanchor='right', y=1.08,
                    font=dict(size=9, color='#a7a7b2'), bgcolor='rgba(0,0,0,0)'),
        showlegend=True,
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False, fixedrange=True,
        tickformat='%b %d' if sessions <= 66 else '%b', nticks=5,
        tickfont=dict(color='#767682', size=9),
        rangebreaks=[dict(bounds=['sat', 'mon'])]
    )
    fig.update_yaxes(
        side='right', showgrid=True, gridcolor='rgba(255,255,255,.07)',
        zeroline=False, fixedrange=True, tickprefix='$', nticks=6,
        tickfont=dict(color='#767682', size=9)
    )
    return fig


def classify_regime(frame: pd.DataFrame) -> pd.Series:
    """Classify price structure using only information available on each date."""
    close, ma20, ma50, ma200 = (frame['Close'], frame['MA20'],
                                frame['MA50'], frame['MA200'])
    conditions = [
        (close > ma20) & (ma20 > ma50) & (ma50 > ma200),
        (close < ma20) & (ma20 < ma50) & (ma50 < ma200),
        (close > ma20) & (ma20 > ma50) & (close < ma200),
        (close < ma20) & (ma50 > ma200),
    ]
    labels = ['Uptrend', 'Downtrend', 'Recovery', 'Pullback']
    return pd.Series(np.select(conditions, labels, default='Range'), index=frame.index)


def historical_evidence(frame: pd.DataFrame) -> tuple[str, list[dict]]:
    """Summarize forward returns after historical observations in today's regime."""
    work = frame.copy()
    work['Regime'] = classify_regime(work)
    current = str(work['Regime'].iloc[-1])
    rows = []
    return_close = work['ReturnClose'] if 'ReturnClose' in work else work['Close']
    for sessions in (5, 20, 60):
        work[f'Fwd{sessions}'] = return_close.shift(-sessions) / return_close - 1
        candidates = work.loc[work['Regime'].eq(current), f'Fwd{sessions}'].dropna()
        # Space observations by their horizon to reduce overlapping-return inflation.
        sample = candidates.iloc[::sessions]
        rows.append({
            'horizon': f'{sessions} sessions',
            'sample': int(len(sample)),
            'reliability': ('Moderate' if len(sample) >= 30 else
                            'Limited' if len(sample) >= 10 else 'Very limited'),
            'median': float(sample.median() * 100) if len(sample) else np.nan,
            'hit_rate': float((sample > 0).mean() * 100) if len(sample) else np.nan,
            'worst': float(sample.quantile(.10) * 100) if len(sample) else np.nan,
        })
    return current, rows


def risk_snapshot(frame: pd.DataFrame) -> dict:
    close = (frame['ReturnClose'] if 'ReturnClose' in frame else frame['Close']).dropna()
    returns = close.pct_change().dropna()
    one_year = close.tail(252)
    drawdown = one_year / one_year.cummax() - 1
    return {
        'vol20': finite(returns.tail(20).std() * np.sqrt(252) * 100),
        'vol60': finite(returns.tail(60).std() * np.sqrt(252) * 100),
        'max_drawdown': finite(drawdown.min() * 100),
        'var95': finite(returns.tail(252).quantile(.05) * 100),
        'from_high': finite((close.iloc[-1] / one_year.max() - 1) * 100),
    }


def data_quality(frame: pd.DataFrame) -> dict:
    """Run basic integrity and freshness checks before displaying analytics."""
    issues = []
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    latest = frame[required].tail(252)
    if latest.isna().any().any():
        issues.append('missing OHLCV values')
    bad_ohlc = ((latest['High'] < latest[['Open', 'Close', 'Low']].max(axis=1)) |
                (latest['Low'] > latest[['Open', 'Close', 'High']].min(axis=1)))
    if bad_ohlc.any():
        issues.append('invalid OHLC relationship')
    if frame.index.duplicated().any():
        issues.append('duplicate dates')
    as_of = pd.Timestamp(frame.index[-1]).tz_localize(None).normalize()
    today = pd.Timestamp.now().tz_localize(None).normalize()
    age_days = int((today - as_of).days)
    if age_days > 4:
        issues.append(f'latest bar is {age_days} days old')
    return {
        'status': 'PASS' if not issues else 'CHECK',
        'issues': issues,
        'age_days': age_days,
        'as_of': as_of.strftime('%b %d, %Y'),
    }


# ── Mobile-first application ──────────────────────────────────
if 'ticker_input' not in st.session_state:
    st.session_state.ticker_input = 'META'

with st.expander("Tracking settings", expanded=False):
    ticker = st.text_input(
        "Ticker", key="ticker_input", placeholder="META, AAPL, NVDA"
    ).upper().strip()
    settings_left, settings_right = st.columns(2)
    with settings_left:
        chart_window = st.selectbox("Chart range", ["1M", "3M", "6M", "1Y"], index=1)
    with settings_right:
        horizon = st.selectbox(
            "Review horizon",
            ["Tactical (1–10 days)", "Swing (2–8 weeks)", "Position (2–12 months)"],
            index=1
        )
    if st.button("Refresh market data", width="stretch"):
        st.cache_data.clear()
        st.rerun()

if not ticker:
    st.info("Enter a ticker to continue.")
    st.stop()

with st.spinner(f"Loading {ticker} market data…"):
    try:
        df = compute_signals(fetch_data(ticker, period="5y"))
        provider = df.attrs.get('provider', 'Unknown')
        plan = build_trade_plan(df, 10_000, 1.0, horizon)
        sent_avg, news_items = get_sentiment(ticker)
    except Exception as exc:
        st.error(f"Unable to load **{html.escape(ticker)}**. Check the symbol and connection.")
        with st.expander("Technical details"):
            st.code(str(exc))
        st.stop()

try:
    info = yf.Ticker(ticker).info or {}
except Exception:
    info = {}

cur = finite(df['Close'].iloc[-1])
prev = finite(df['Close'].iloc[-2], cur)
chg_1d = (cur - prev) / prev * 100 if prev else 0
chg_20d = (cur / finite(df['Close'].iloc[-21], cur) - 1) * 100
sig = str(df['Signal'].iloc[-1])
rsi = finite(df['RSI'].iloc[-1], 50)
atr = finite(df['ATR'].iloc[-1], cur * .02)
atr_p = atr / cur * 100 if cur else 0
vol = finite(df['Volume'].iloc[-1])
vol_ma = finite(df['Volume_MA20'].iloc[-1], vol)

safe_ticker = html.escape(ticker)
company = html.escape(str(info.get('shortName') or ticker))
market_cap = finite(info.get('marketCap'))
market_cap_text = f"${market_cap/1e12:.2f}T" if market_cap >= 1e12 else f"${market_cap/1e9:.1f}B" if market_cap else "—"
avg_volume = finite(info.get('averageVolume'), vol_ma)
avg_volume_text = f"{avg_volume/1e6:.1f}M" if avg_volume else "—"
week_high = finite(info.get('fiftyTwoWeekHigh'), df['High'].tail(252).max())
week_low = finite(info.get('fiftyTwoWeekLow'), df['Low'].tail(252).min())
pe = finite(info.get('trailingPE'))
beta = finite(info.get('beta'))
day_low = finite(df['Low'].iloc[-1])
day_high = finite(df['High'].iloc[-1])
data_as_of = pd.Timestamp(df.index[-1]).strftime('%b %d, %Y')
change_class = 'positive' if chg_1d >= 0 else 'negative'
regime, evidence_rows = historical_evidence(df)
risk = risk_snapshot(df)
ma20 = finite(df['MA20'].iloc[-1], cur)
ma50 = finite(df['MA50'].iloc[-1], cur)
ma200 = finite(df['MA200'].iloc[-1], cur)
macd = finite(df['MACD'].iloc[-1])
macd_signal = finite(df['MACD_signal'].iloc[-1])
alignment_label = ('Positive' if cur > ma20 > ma50 > ma200 else
                   'Negative' if cur < ma20 < ma50 < ma200 else 'Mixed')
quality = data_quality(df)
quality_note = ', '.join(quality['issues']) if quality['issues'] else 'No structural OHLCV errors detected'
returns_by_horizon = {
    '1 week': (cur / finite(df['Close'].iloc[-6], cur) - 1) * 100,
    '1 month': chg_20d,
    '3 months': (cur / finite(df['Close'].iloc[-61], cur) - 1) * 100,
    '1 year': (cur / finite(df['Close'].iloc[-252], cur) - 1) * 100,
}

st.markdown(f"""
<div class="mobile-nav">
  <div class="ticker-identity">
    <div class="ticker-monogram">{safe_ticker[:2]}</div>
    <div class="ticker-lockup">
      <div class="ticker-name">{safe_ticker}</div>
      <div class="ticker-company">{company}</div>
    </div>
  </div>
  <div class="market-pill"><span class="market-dot"></span>DAILY DATA</div>
</div>
""", unsafe_allow_html=True)

tab_price, tab_trend, tab_momentum, tab_risk, tab_evidence, tab_company, tab_news = st.tabs([
    "Price", "Trend", "Momentum", "Risk", "Evidence", "Company", "News"
])

with tab_price:
    if cur < plan['entry_low']:
        price_guide = (
            "Price is below the potential buy zone. A lower price is not automatically "
            "safer—wait for the price to stabilize before making a decision."
        )
    elif cur <= plan['entry_high']:
        price_guide = (
            "Price is inside the potential buy zone. Watch whether it holds this area; "
            "a zone is not a guarantee that the price will bounce."
        )
    elif cur < plan['target_1']:
        price_guide = (
            "Price is between the buy and sell watch zones. This is usually a wait-and-review "
            "area rather than an obvious entry or exit."
        )
    elif cur <= plan['target_2']:
        price_guide = (
            "Price is inside the potential sell / profit-taking zone. If you already own it, "
            "review whether to hold or reduce; this is not a guaranteed top."
        )
    else:
        price_guide = (
            "Price is above the potential sell zone. Momentum may continue, but reversal risk "
            "is higher; review the position instead of assuming it must keep rising."
        )

    st.markdown(f"""
    <div class="price-panel">
      <div class="eyebrow">Latest close · {data_as_of}</div>
      <div class="hero-price">${cur:.2f}</div>
      <div class="{change_class}">{chg_1d:+.2f}% <span class="mini-copy">last session</span></div>
    </div>
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-label">Current regime</div><div class="stat-value">{regime}</div></div>
      <div class="stat-cell"><div class="stat-label">Data integrity</div><div class="stat-value">{quality['status']}</div></div>
    </div>
    <div class="detail-card">
      <div class="detail-row"><span>Provider</span><b>{provider}</b></div>
      <div class="detail-row"><span>Price type</span><b>Official daily close · USD</b></div>
      <div class="detail-row"><span>As of</span><b>{quality['as_of']}</b></div>
      <div class="detail-row"><span>Integrity check</span><b>{quality_note}</b></div>
    </div>
    """, unsafe_allow_html=True)

    chart = build_mobile_chart(df, chart_window)
    st.plotly_chart(chart, width='stretch', config={
        'displayModeBar': False, 'displaylogo': False, 'scrollZoom': False,
        'responsive': True
    })

    st.markdown(f"""
    <div class="eyebrow" style="margin:16px 3px 8px;">SIMPLE PRICE GUIDE · RESEARCH ONLY</div>
    <div class="plan-strip">
      <div class="mobile-card"><div class="eyebrow">Potential buy zone</div><div class="value lime">${plan['entry_low']:.2f}–${plan['entry_high']:.2f}</div></div>
      <div class="mobile-card"><div class="eyebrow">Potential sell / trim zone</div><div class="value purple">${plan['target_1']:.2f}–${plan['target_2']:.2f}</div></div>
    </div>
    <div class="mobile-card" style="margin-top:7px;">
      <div class="eyebrow">If price falls below</div>
      <div class="value red">${plan['stop']:.2f}</div>
      <div class="mini-copy">Reconsider the idea and review risk. This is not an automatic sell order.</div>
    </div>
    <div class="detail-card" style="margin-top:9px;">
      <div class="detail-row"><span>What this means now</span><b>${cur:.2f}</b></div>
      <div class="mobile-note" style="padding:11px 0;">{price_guide}</div>
    </div>
    <div class="mobile-note">These ranges are calculated from recent price structure and volatility. They help users plan what to watch; they are not personalized advice, guaranteed prices or automatic orders.</div>
    """, unsafe_allow_html=True)

    with st.expander("How to read this page"):
        st.markdown(f"""
**Latest close** tells you what happened in the most recent completed session—not what happens next.

**{regime} regime** describes the current price structure. `Range` means price is moving without clean one-way moving-average alignment.

**Candlesticks** show each session's open, high, low and close. The purple line is the 20-session average; being above it describes relative position, not a promise of further gains.

**Potential buy zone** is the nearby area where price may find support. Consider it only if price begins to stabilize; it is not a guaranteed bargain.

**Potential sell / trim zone** is where recent price history suggests selling pressure may increase. If you already own the security, this is an area to review profit-taking—not a guaranteed top.

**If price falls below** marks where the current idea may no longer be working and deserves a risk review. It is not an automatic sell order.
        """)

with tab_trend:
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-label">Price regime</div><div class="stat-value">{regime}</div></div>
      <div class="stat-cell"><div class="stat-label">MA alignment</div><div class="stat-value">{alignment_label}</div></div>
      <div class="stat-cell"><div class="stat-label">Price vs. 20D</div><div class="stat-value">{(cur/ma20-1)*100:+.2f}%</div></div>
      <div class="stat-cell"><div class="stat-label">Price vs. 200D</div><div class="stat-value">{(cur/ma200-1)*100:+.2f}%</div></div>
    </div>
    <div class="detail-card">
      <div class="detail-row"><span>20-day average</span><b>${ma20:.2f}</b></div>
      <div class="detail-row"><span>50-day average</span><b>${ma50:.2f}</b></div>
      <div class="detail-row"><span>200-day average</span><b>${ma200:.2f}</b></div>
      <div class="detail-row"><span>Trend alignment</span><b>{alignment_label}</b></div>
    </div>
    <div class="eyebrow" style="margin:18px 3px 8px;">TRAILING RETURNS</div>
    <div class="detail-card">
      <div class="detail-row"><span>1 week</span><b>{returns_by_horizon['1 week']:+.2f}%</b></div>
      <div class="detail-row"><span>1 month</span><b>{returns_by_horizon['1 month']:+.2f}%</b></div>
      <div class="detail-row"><span>3 months</span><b>{returns_by_horizon['3 months']:+.2f}%</b></div>
      <div class="detail-row"><span>1 year</span><b>{returns_by_horizon['1 year']:+.2f}%</b></div>
    </div>
    """, unsafe_allow_html=True)

with tab_momentum:
    macd_state = "Above signal" if macd > macd_signal else "Below signal"
    rsi_state = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-label">RSI (14)</div><div class="stat-value">{rsi:.1f}</div></div>
      <div class="stat-cell"><div class="stat-label">RSI state</div><div class="stat-value">{rsi_state}</div></div>
      <div class="stat-cell"><div class="stat-label">MACD</div><div class="stat-value">{macd:.2f}</div></div>
      <div class="stat-cell"><div class="stat-label">Volume ratio</div><div class="stat-value">{vol/vol_ma:.2f}×</div></div>
    </div>
    <div class="detail-card">
      <div class="detail-row"><span>MACD signal</span><b>{macd_signal:.2f}</b></div>
      <div class="detail-row"><span>MACD position</span><b>{macd_state}</b></div>
      <div class="detail-row"><span>20-session return</span><b>{chg_20d:+.2f}%</b></div>
      <div class="detail-row"><span>Latest volume</span><b>{vol/1e6:.1f}M</b></div>
      <div class="detail-row"><span>20D average volume</span><b>{vol_ma/1e6:.1f}M</b></div>
    </div>
    <div class="mobile-note">Momentum confirms or contradicts trend; it does not establish fair value and can reverse quickly around news or earnings.</div>
    """, unsafe_allow_html=True)

with tab_risk:
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-label">20D annualized vol.</div><div class="stat-value">{risk['vol20']:.1f}%</div></div>
      <div class="stat-cell"><div class="stat-label">60D annualized vol.</div><div class="stat-value">{risk['vol60']:.1f}%</div></div>
      <div class="stat-cell"><div class="stat-label">1Y max drawdown</div><div class="stat-value">{risk['max_drawdown']:.1f}%</div></div>
      <div class="stat-cell"><div class="stat-label">From 1Y high</div><div class="stat-value">{risk['from_high']:.1f}%</div></div>
    </div>
    <div class="detail-card">
      <div class="detail-row"><span>ATR (14)</span><b>${atr:.2f}</b></div>
      <div class="detail-row"><span>ATR / price</span><b>{atr_p:.2f}%</b></div>
      <div class="detail-row"><span>Historical 95% daily VaR</span><b>{risk['var95']:.2f}%</b></div>
      <div class="detail-row"><span>Beta</span><b>{f'{beta:.2f}' if beta else '—'}</b></div>
      <div class="detail-row"><span>Reference risk threshold</span><b>${plan['stop']:.2f}</b></div>
    </div>
    <div class="mobile-note">Historical VaR means roughly 5% of observed sessions were worse than this return. It is not a maximum-loss estimate; gaps and crises can be much worse.</div>
    """, unsafe_allow_html=True)

with tab_evidence:
    evidence_html = ''.join(
        f"""<div class="detail-card">
          <div class="detail-row"><span>Forward horizon</span><b>{row['horizon']}</b></div>
          <div class="detail-row"><span>Historical observations</span><b>{row['sample']}</b></div>
          <div class="detail-row"><span>Sample quality</span><b>{row['reliability']}</b></div>
          <div class="detail-row"><span>Median forward return</span><b>{row['median']:+.2f}%</b></div>
          <div class="detail-row"><span>Positive-return frequency</span><b>{row['hit_rate']:.1f}%</b></div>
          <div class="detail-row"><span>10th-percentile outcome</span><b>{row['worst']:+.2f}%</b></div>
        </div>"""
        for row in evidence_rows
    )
    st.markdown(f"""
    <div class="price-panel">
      <div class="eyebrow">CURRENT PRICE-STRUCTURE REGIME</div>
      <div class="hero-price" style="font-size:25px;">{regime}</div>
      <div class="mini-copy">Historical analogs from this ticker's downloaded history</div>
    </div>
    {evidence_html}
    <div class="mobile-note">Evidence is descriptive, not a forecast. Observations are spaced by the forward horizon to reduce overlap, but small samples, regime change and repeated testing can still mislead. A credible model must later be tested on unseen data and against a benchmark.</div>
    """, unsafe_allow_html=True)

with tab_company:
    sector_text = html.escape(str(info.get('sector') or '—'))
    industry_text = html.escape(str(info.get('industry') or '—'))
    employees = finite(info.get('fullTimeEmployees'))
    revenue_growth = finite(info.get('revenueGrowth'))
    profit_margin = finite(info.get('profitMargins'))
    summary = html.escape(str(info.get('longBusinessSummary') or 'No company summary was returned.'))
    if len(summary) > 900:
        summary = summary[:897] + '…'
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-label">Market cap</div><div class="stat-value">{market_cap_text}</div></div>
      <div class="stat-cell"><div class="stat-label">P/E ratio</div><div class="stat-value">{f'{pe:.1f}×' if pe else '—'}</div></div>
      <div class="stat-cell"><div class="stat-label">52-week range</div><div class="stat-value">${week_low:.2f}–${week_high:.2f}</div></div>
      <div class="stat-cell"><div class="stat-label">Average volume</div><div class="stat-value">{avg_volume_text}</div></div>
    </div>
    <div class="detail-card">
      <div class="detail-row"><span>Sector</span><b>{sector_text}</b></div>
      <div class="detail-row"><span>Industry</span><b>{industry_text}</b></div>
      <div class="detail-row"><span>Employees</span><b>{f'{employees:,.0f}' if employees else '—'}</b></div>
      <div class="detail-row"><span>Revenue growth</span><b>{f'{revenue_growth*100:+.1f}%' if revenue_growth else '—'}</b></div>
      <div class="detail-row"><span>Profit margin</span><b>{f'{profit_margin*100:.1f}%' if profit_margin else '—'}</b></div>
    </div>
    <div class="mobile-card" style="margin-top:8px;"><div class="eyebrow">BUSINESS SUMMARY</div><div style="font-size:10px;line-height:1.6;color:#55555f;margin-top:8px;">{summary}</div></div>
    """, unsafe_allow_html=True)

with tab_news:
    sentiment_label = "Positive" if sent_avg > .1 else "Negative" if sent_avg < -.1 else "Neutral"
    st.markdown(f"""
    <div class="price-panel">
      <div class="eyebrow">HEADLINE PULSE</div>
      <div class="hero-price" style="font-size:25px;">{sentiment_label}</div>
      <div class="mini-copy">Average polarity {sent_avg:+.3f} · {len(news_items)} English-language headlines</div>
    </div>
    """, unsafe_allow_html=True)
    if news_items:
        for item in news_items[:8]:
            polarity = finite(item['polarity'])
            title = html.escape(str(item['title']))
            tone = "Positive" if polarity > .1 else "Negative" if polarity < -.1 else "Neutral"
            st.markdown(f"""
            <div class="detail-card">
              <div style="font-size:11px;color:#171821;line-height:1.45;padding:7px 0;">{title}</div>
              <div class="mini-copy" style="padding-bottom:7px;">{tone} · {polarity:+.3f}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No analyzable headlines were returned.")
    st.markdown('<div class="mobile-note">Headline polarity is a rough language score. It does not judge source quality, materiality, novelty or whether the information is already reflected in price.</div>', unsafe_allow_html=True)

# ── Tracking disclaimer ───────────────────────────────────────
st.markdown(
    '<div class="mobile-note">Delayed market data for research only. No broker is connected. '
    'This tracker organizes technical, risk, historical and company evidence. It does not predict the future or provide personalized investment advice.</div>',
    unsafe_allow_html=True
)

# The mobile experience above is the active application entry point.
st.stop()
