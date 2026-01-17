import os, time, pandas as pd, numpy as np
from sqlalchemy import create_engine, text
import streamlit as st

# ---------- Config ----------
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_DB   = os.getenv("POSTGRES_DB", "crypto")
DB_USER = os.getenv("POSTGRES_USER", "crypto")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "crypto")
REFRESH_MS = int(os.getenv("REFRESH_MS", "30000"))

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_DB}")

st.set_page_config(page_title="Real-Time Crypto Dashboard", layout="wide")
st.title("📈 Real-Time Crypto Analytics")
st.caption("Kafka → Postgres → Streamlit • Live KPIs + Forecast (Prophet)")

# ---------- Cached helpers ----------
@st.cache_data(ttl=15, show_spinner=False)
def get_all_coins():
    with engine.connect() as conn:
        q = text("SELECT DISTINCT coin_id FROM prices ORDER BY coin_id;")
        df = pd.read_sql(q, conn)
    return df["coin_id"].tolist()

@st.cache_data(ttl=15, show_spinner=False)
def search_coin_ids(q: str):
    q = (q or "").strip()
    if not q:
        return []
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT DISTINCT coin_id FROM prices WHERE coin_id ILIKE :q ORDER BY coin_id LIMIT 25"),
            conn,
            params={"q": f"%{q}%"},
        )
    return df["coin_id"].tolist()

@st.cache_data(ttl=15, show_spinner=False)
def load_coin_window(coin_id: str, minutes: int):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT ts_epoch_ms, coin_id, symbol, name, current_price, pct_24h
                FROM prices
                WHERE coin_id = :coin_id
                  AND ts_epoch_ms >= (EXTRACT(EPOCH FROM NOW()) * 1000 - :lookback_ms)
                ORDER BY ts_epoch_ms
            """),
            conn,
            params={"coin_id": coin_id, "lookback_ms": minutes * 60 * 1000},
        )
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts_epoch_ms"], unit="ms")
    return df

@st.cache_data(ttl=15, show_spinner=False)
def load_data(minutes: int):
    with engine.connect() as conn:
        q = text("""
            SELECT ts_epoch_ms, coin_id, symbol, name, vs_currency, current_price, market_cap, total_volume, pct_24h
            FROM prices
            WHERE ts_epoch_ms >= (EXTRACT(EPOCH FROM NOW()) * 1000 - :lookback_ms)
        """)
        df = pd.read_sql(q, conn, params={"lookback_ms": minutes * 60 * 1000})
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts_epoch_ms"], unit="ms")
    return df
# -------------------------------------

# ---------- Sidebar: selection & search ----------
st.sidebar.header("Filters")

all_coins = get_all_coins()

# init session state (only when key missing)
if "coins" not in st.session_state:
    st.session_state.coins = list(all_coins)                 # canonical selection
if "coins_picker_widget" not in st.session_state:
    st.session_state.coins_picker_widget = list(all_coins)   # widget state
if "search_query" not in st.session_state:
    st.session_state.search_query = ""                       # persist search text

# callbacks (do not touch search_query here)
def _select_all():
    st.session_state.coins = list(all_coins)
    st.session_state.coins_picker_widget = list(all_coins)

def _clear_all():
    st.session_state.coins = []
    st.session_state.coins_picker_widget = []

def _add_coin(coin_id: str):
    if coin_id and coin_id not in st.session_state.coins:
        st.session_state.coins.append(coin_id)
        st.session_state.coins_picker_widget = list(st.session_state.coins)

colA, colB = st.sidebar.columns(2)
colA.button("Select all", on_click=_select_all)
colB.button("Clear all",  on_click=_clear_all)

# multiselect (read only; widget owns its key)
selected = st.sidebar.multiselect(
    "Coins",
    options=all_coins,
    default=st.session_state.coins_picker_widget,
    key="coins_picker_widget",
)
# sync canonical from widget
st.session_state.coins = list(selected)
coins = st.session_state.coins

window_mins = st.sidebar.slider("Lookback (minutes)", 10, 180, 60)
st.sidebar.write("Auto-refresh:", f"{REFRESH_MS/1000:.0f}s")
st.sidebar.divider()

# gentle nudge for auto-refresh
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=REFRESH_MS, key="auto-refresh")

# Search UI (persists via key)
st.sidebar.markdown("### 🔎 Search a coin")
query = st.sidebar.text_input("Type coin id (e.g., dogecoin, pepe, toncoin)", key="search_query")
suggestions = search_coin_ids(query) if query else []

if query and not suggestions:
    st.sidebar.info("No matches. Try another term.")
elif suggestions:
    picked = st.sidebar.selectbox("Matches", suggestions, key="search_pick")
    st.sidebar.button(
        f"Add {picked} to selection",
        key=f"add_{picked}",
        on_click=_add_coin,
        args=(picked,),
    )
# -------------------------------------

# ---------- Data load & guards ----------
df = load_data(window_mins)
if df.empty:
    st.info("Waiting for data... Make sure your API key is set and services are running.")
    st.stop()

if not coins:
    st.info("No coins selected. Use the sidebar to add coins or click **Select all**.")
    st.stop()
# -------------------------------------

# ---------- Per-coin charts (with metrics at the start) ----------
st.subheader("Live Price Chart — per coin")

# latest snapshot for quick metrics per coin
_latest = (
    df.sort_values("ts")
    .groupby("coin_id")
    .tail(1)
    .set_index("coin_id")[["current_price", "pct_24h"]]
)

def _chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# render cards + charts (3 per row looks nice; change to 2/4 if you prefer)
for row_coins in _chunk(coins, 3):
    cols = st.columns(len(row_coins))
    for i, c in enumerate(row_coins):
        sub = df[df["coin_id"] == c].sort_values("ts")
        if sub.empty:
            continue
        with cols[i]:
            # metric right under the header, before the chart
            if c in _latest.index:
                price = _latest.loc[c, "current_price"]
                delta = (_latest.loc[c, "pct_24h"] or 0)
                st.metric(label=f"{c.title()} Price", value=f"{price:,.4f}", delta=f"{delta:+.2f}%")
            # chart
            st.line_chart(sub, x="ts", y="current_price", height=260)

# ---------- Combined charts ----------
st.subheader("Live Price Chart — combined (all selected)")
combo = df[df["coin_id"].isin(coins)][["ts", "coin_id", "current_price"]].copy()

if combo.empty:
    st.info("No data to plot yet for the selected coins.")
else:
    combo["ts"] = combo["ts"].dt.floor("min")
    wide = (
        combo.pivot_table(index="ts", columns="coin_id", values="current_price", aggfunc="last")
        .sort_index()
    )
    wide = wide.asfreq("1min").ffill(limit=5)

    st.markdown("**Raw prices (aligned to 1-min)**")
    st.line_chart(wide, height=360)

    st.markdown("**Indexed to 100 at window start (shape comparison)**")
    norm = wide / wide.iloc[0] * 100.0
    st.line_chart(norm, height=360)

# ---------- Forecast ----------
st.subheader("Short-Term Forecast (Demo)")
sel = st.selectbox("Select coin for forecast", options=coins, index=0)
sub = (
    df[df["coin_id"] == sel][["ts", "current_price"]]
    .dropna()
    .drop_duplicates(subset="ts")
    .sort_values("ts")
)
if len(sub) >= 20:
    try:
        from prophet import Prophet
        fdf = sub.rename(columns={"ts": "ds", "current_price": "y"})
        m = Prophet(daily_seasonality=True, weekly_seasonality=True)
        m.fit(fdf)
        future = m.make_future_dataframe(periods=30, freq="min")
        fcst = m.predict(future).tail(60)[["ds", "yhat", "yhat_lower", "yhat_upper"]].set_index("ds")
        st.line_chart(fcst, height=360)
        st.caption("Prophet forecast (~60 mins)")
    except Exception as e:
        st.warning(f"Prophet unavailable ({e}). Falling back to EWMA.")
        ewma = sub.set_index("ts")["current_price"].ewm(span=10).mean()
        st.line_chart(ewma, height=360)
else:
    st.info("Need ~20 points to forecast. Keep the pipeline running a few minutes.")
