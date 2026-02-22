import os
import sys
import json
import threading

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "src"))
sys.path.insert(1, os.path.join(base_dir, "tests"))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import algorithms.EMA as ema_mod
import algorithms.MACD as macd_mod
import algorithms.RSI as rsi_mod
import algorithms.AROON as aroon_mod
import testAlgorithms.testGoldenCross as gc_mod

from algorithms.MACD import macd
from algorithms.RSI import rsi
from algorithms.AROON import aroon
from testAlgorithms.testGoldenCross import goldenCross

app = FastAPI(title="Trading Algorithm Tester")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

_run_lock = threading.Lock()

ALGORITHMS = {
    "macd": {"name": "MACD", "has_subplot": True},
    "rsi": {"name": "RSI", "has_subplot": True},
    "aroon": {"name": "Aroon", "has_subplot": True},
    "golden_cross": {"name": "Golden Cross (EMA 50/200)", "has_subplot": False},
}

ALGO_FUNCS = {
    "macd": macd,
    "rsi": rsi,
    "aroon": aroon,
    "golden_cross": goldenCross,
}

STOCK_COLORS = [
    "#4FC3F7", "#FF9800", "#ce93d8", "#FFD54F",
    "#4DD0E1", "#FF7043", "#AED581", "#F48FB1",
    "#90CAF9", "#FFCC80", "#B39DDB", "#80CBC4",
]


class RunRequest(BaseModel):
    symbols: list[str]
    algorithms: list[str]
    start_date: str = "2025-01-11"
    interval: str = "1h"
    macd_sensitivity: int = 0


def reset_state():
    """Reset all algorithm global state for a fresh run."""
    ema_mod.prevEMA = {}

    macd_mod.prevMACD = 0.0
    macd_mod.prevSignal = 0.0
    macd_mod.macdList = []
    macd_mod.signalList = []

    rsi_mod.priceCount = 0
    rsi_mod.prevPrice = 0.0
    rsi_mod.prevAvgLoss = 0.0
    rsi_mod.prevAvgGain = 0.0
    rsi_mod.rsiList = []

    aroon_mod.previousAroon = 0.0
    aroon_mod.priceList = []
    aroon_mod.aroonList = []

    gc_mod.prevEma50 = 0.0
    gc_mod.prevEma200 = 0.0
    gc_mod.initialLow = 0.0
    gc_mod.intermediaryHigh = 0.0
    gc_mod.lowBroken = False
    gc_mod.prevPrices = []


def _run_single_backtest(symbol, algo_id, prices, dates, macd_sensitivity):
    """Run one symbol+algorithm combination and return rich result data."""
    reset_state()

    algo_func = ALGO_FUNCS[algo_id]
    capital = 1000.0
    starting_capital = 1000.0
    buy_points = []
    sell_points = []
    shares = 0.0
    has_bought = False
    ema50_list = []
    ema200_list = []
    base_price = prices[0] if prices else 1
    pct_prices = []

    for i, price in enumerate(prices):
        pct = 100 * (price - base_price) / base_price if base_price != 0 else 0
        pct_prices.append(pct)

        if algo_id == "macd":
            action = algo_func(price, macd_sensitivity)
        else:
            action = algo_func(price)

        if algo_id == "golden_cross":
            ema50_list.append(ema_mod.prevEMA.get("50", price))
            ema200_list.append(ema_mod.prevEMA.get("200", price))

        if i > 30 and action != 0:
            if action == 1 and has_bought:
                capital += shares * price
                sell_points.append({"date": dates[i], "price": price, "pct": pct})
                has_bought = False
                shares = 0.0
            elif action == 2 and not has_bought:
                shares = capital / price
                buy_points.append({"date": dates[i], "price": price, "pct": pct})
                has_bought = True
                capital -= shares * price
        elif i == len(prices) - 1 and has_bought:
            capital += shares * price
            sell_points.append({"date": dates[i], "price": price, "pct": pct})
            has_bought = False
            shares = 0.0

    total_change = capital - starting_capital
    pct_algo = 100 * total_change / starting_capital
    pct_stock = 100 * (prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0

    indicator_data = {}
    if algo_id == "macd":
        indicator_data = {
            "macd_list": list(macd_mod.macdList),
            "signal_list": list(macd_mod.signalList),
        }
    elif algo_id == "rsi":
        indicator_data = {"rsi_list": list(rsi_mod.rsiList)}
    elif algo_id == "aroon":
        indicator_data = {"aroon_list": list(aroon_mod.aroonList)}
    elif algo_id == "golden_cross":
        indicator_data = {
            "ema50_list": list(ema50_list),
            "ema200_list": list(ema200_list),
        }

    return {
        "symbol": symbol,
        "prices": prices,
        "dates": dates,
        "pct_prices": pct_prices,
        "buy_points": buy_points,
        "sell_points": sell_points,
        "indicator_data": indicator_data,
        "metrics": {
            "symbol": symbol,
            "algo_return_pct": round(pct_algo, 2),
            "stock_return_pct": round(pct_stock, 2),
            "starting_capital": starting_capital,
            "ending_capital": round(capital, 2),
            "num_buys": len(buy_points),
            "num_sells": len(sell_points),
        },
    }


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api/algorithms")
async def get_algorithms():
    return [{"id": k, "name": v["name"]} for k, v in ALGORITHMS.items()]


@app.post("/api/run")
def run_algorithm(req: RunRequest):
    with _run_lock:
        symbols = list(dict.fromkeys(
            s.strip().upper() for s in req.symbols if s.strip()
        ))
        algorithms = [a for a in req.algorithms if a in ALGORITHMS]

        if not symbols:
            return JSONResponse(
                status_code=400,
                content={"error": "At least one stock symbol is required."},
            )
        if not algorithms:
            return JSONResponse(
                status_code=400,
                content={"error": "At least one algorithm must be selected."},
            )

        stock_data = {}
        errors = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=req.start_date, interval=req.interval)
                if data.empty:
                    errors.append(f"No data found for {symbol}")
                    continue
                stock_data[symbol] = {
                    "prices": data["Close"].tolist(),
                    "dates": data.index.strftime("%Y-%m-%d %H:%M").tolist(),
                }
            except Exception as e:
                errors.append(f"Failed to fetch {symbol}: {e}")

        if not stock_data:
            return JSONResponse(
                status_code=400,
                content={"error": "; ".join(errors) if errors else "No valid symbols provided."},
            )

        multi_stock = len(stock_data) > 1
        results = []

        for algo_id in algorithms:
            stock_runs = []
            for symbol, sd in stock_data.items():
                run = _run_single_backtest(
                    symbol, algo_id,
                    sd["prices"], sd["dates"],
                    req.macd_sensitivity,
                )
                stock_runs.append(run)

            fig = _build_combined_figure(algo_id, stock_runs, multi_stock)

            total_starting = sum(r["metrics"]["starting_capital"] for r in stock_runs)
            total_ending = sum(r["metrics"]["ending_capital"] for r in stock_runs)
            portfolio_return = (
                round(100 * (total_ending - total_starting) / total_starting, 2)
                if total_starting else 0
            )
            avg_stock_return = round(
                sum(r["metrics"]["stock_return_pct"] for r in stock_runs) / len(stock_runs), 2
            )

            results.append({
                "plot": json.loads(fig.to_json()),
                "multi_stock": multi_stock,
                "stock_colors": STOCK_COLORS[:len(stock_runs)],
                "portfolio_metrics": {
                    "algorithm": ALGORITHMS[algo_id]["name"],
                    "portfolio_return_pct": portfolio_return,
                    "avg_stock_return_pct": avg_stock_return,
                    "starting_capital": total_starting,
                    "ending_capital": round(total_ending, 2),
                    "total_buys": sum(r["metrics"]["num_buys"] for r in stock_runs),
                    "total_sells": sum(r["metrics"]["num_sells"] for r in stock_runs),
                    "num_stocks": len(stock_runs),
                },
                "stock_metrics": [r["metrics"] for r in stock_runs],
            })

        return {"results": results, "errors": errors}


def _build_combined_figure(algo_id, stock_runs, multi_stock):
    algo = ALGORITHMS[algo_id]
    has_subplot = algo["has_subplot"]
    n = len(stock_runs)

    if n == 1:
        price_title = f"{stock_runs[0]['symbol']} Price"
    else:
        price_title = "Price (% Change from Start)"

    if has_subplot:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            subplot_titles=[price_title, algo["name"]],
        )
    else:
        fig = go.Figure()

    def _add(trace, subplot_row=None):
        if has_subplot and subplot_row:
            fig.add_trace(trace, row=subplot_row, col=1)
        elif has_subplot:
            fig.add_trace(trace, row=1, col=1)
        else:
            fig.add_trace(trace)

    for idx, sr in enumerate(stock_runs):
        color = STOCK_COLORS[idx % len(STOCK_COLORS)]
        symbol = sr["symbol"]

        if multi_stock:
            price_y = sr["pct_prices"]
            buy_y = [p["pct"] for p in sr["buy_points"]]
            sell_y = [p["pct"] for p in sr["sell_points"]]
        else:
            price_y = sr["prices"]
            buy_y = [p["price"] for p in sr["buy_points"]]
            sell_y = [p["price"] for p in sr["sell_points"]]

        _add(go.Scatter(
            x=sr["dates"], y=price_y,
            mode="lines",
            name=symbol if multi_stock else f"{symbol} Price",
            line=dict(color=color, width=1.5),
            legendgroup=symbol,
        ))

        if sr["buy_points"]:
            _add(go.Scatter(
                x=[p["date"] for p in sr["buy_points"]],
                y=buy_y,
                mode="markers",
                name=f"{symbol} Buy" if multi_stock else "Buy",
                marker=dict(
                    color="#66BB6A", size=10, symbol="triangle-up",
                    line=dict(width=2, color=color) if multi_stock else dict(width=1, color="#fff"),
                ),
                legendgroup=symbol,
                showlegend=not multi_stock,
            ))

        if sr["sell_points"]:
            _add(go.Scatter(
                x=[p["date"] for p in sr["sell_points"]],
                y=sell_y,
                mode="markers",
                name=f"{symbol} Sell" if multi_stock else "Sell",
                marker=dict(
                    color="#EF5350", size=10, symbol="triangle-down",
                    line=dict(width=2, color=color) if multi_stock else dict(width=1, color="#fff"),
                ),
                legendgroup=symbol,
                showlegend=not multi_stock,
            ))

        ind = sr["indicator_data"]

        if algo_id == "macd" and has_subplot:
            if multi_stock:
                _add(go.Scatter(
                    x=sr["dates"], y=ind["macd_list"],
                    mode="lines", name=f"{symbol} MACD",
                    line=dict(color=color, width=1.5),
                    legendgroup=symbol, showlegend=False,
                ), subplot_row=2)
                _add(go.Scatter(
                    x=sr["dates"], y=ind["signal_list"],
                    mode="lines", name=f"{symbol} Signal",
                    line=dict(color=color, width=1, dash="dot"),
                    legendgroup=symbol, showlegend=False,
                ), subplot_row=2)
            else:
                _add(go.Scatter(
                    x=sr["dates"], y=ind["macd_list"],
                    mode="lines", name="MACD",
                    line=dict(color="#FF9800", width=1.5),
                ), subplot_row=2)
                _add(go.Scatter(
                    x=sr["dates"], y=ind["signal_list"],
                    mode="lines", name="Signal",
                    line=dict(color="#E040FB", width=1.5),
                ), subplot_row=2)
                histogram = [m - s for m, s in zip(ind["macd_list"], ind["signal_list"])]
                bar_colors = ["#66BB6A" if h >= 0 else "#EF5350" for h in histogram]
                _add(go.Bar(
                    x=sr["dates"], y=histogram,
                    name="Histogram", marker_color=bar_colors, opacity=0.5,
                ), subplot_row=2)

        elif algo_id == "rsi" and has_subplot:
            _add(go.Scatter(
                x=sr["dates"], y=ind["rsi_list"],
                mode="lines",
                name=f"{symbol} RSI" if multi_stock else "RSI",
                line=dict(color=color, width=1.5) if multi_stock else dict(color="#FF9800", width=1.5),
                legendgroup=symbol if multi_stock else None,
                showlegend=not multi_stock,
            ), subplot_row=2)

        elif algo_id == "aroon" and has_subplot:
            _add(go.Scatter(
                x=sr["dates"], y=ind["aroon_list"],
                mode="lines",
                name=f"{symbol} Aroon" if multi_stock else "Aroon Oscillator",
                line=dict(color=color, width=1.5) if multi_stock else dict(color="#FF9800", width=1.5),
                legendgroup=symbol if multi_stock else None,
                showlegend=not multi_stock,
            ), subplot_row=2)

        elif algo_id == "golden_cross" and not multi_stock:
            _add(go.Scatter(
                x=sr["dates"], y=ind["ema50_list"],
                mode="lines", name="EMA 50",
                line=dict(color="#FF9800", width=1.5),
            ))
            _add(go.Scatter(
                x=sr["dates"], y=ind["ema200_list"],
                mode="lines", name="EMA 200",
                line=dict(color="#E040FB", width=1.5),
            ))

    if algo_id == "rsi" and has_subplot:
        fig.add_hline(y=70, line_dash="dash", line_color="#EF5350",
                      annotation_text="Overbought (70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#66BB6A",
                      annotation_text="Oversold (30)", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#555", row=2, col=1)
    elif algo_id == "aroon" and has_subplot:
        fig.add_hline(y=0, line_dash="dash", line_color="#555", row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#16213e",
        font=dict(color="#e0e0e0", family="Inter, sans-serif"),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=650 if has_subplot else 480,
    )
    fig.update_xaxes(gridcolor="#1e3a5f", zeroline=False)
    fig.update_yaxes(gridcolor="#1e3a5f", zeroline=False)

    if multi_stock:
        if has_subplot:
            fig.update_yaxes(title_text="% Change", row=1, col=1)
        else:
            fig.update_yaxes(title_text="% Change")

    return fig


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
