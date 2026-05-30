"""
Central configuration — edit .env for secrets, this file for behaviour.
"""
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent


class ExchangeConfig(BaseModel):
    name: str = "binance"
    api_key: str = Field(default_factory=lambda: os.getenv("EXCHANGE_API_KEY", ""))
    api_secret: str = Field(default_factory=lambda: os.getenv("EXCHANGE_API_SECRET", ""))
    sandbox: bool = True  # ALWAYS start in sandbox/paper trading


class RiskConfig(BaseModel):
    max_open_trades: int = 5
    stake_amount_pct: float = 0.02       # 2 % of capital per trade
    max_drawdown_pct: float = 0.15       # Stop all trading if DD > 15 %
    risk_reward_ratio: float = 2.0       # Minimum 1:2 R/R
    trailing_stop_pct: float = 0.03      # 3 % trailing stop
    hard_stop_pct: float = 0.05          # 5 % hard stop loss
    take_profit_pct: float = 0.06        # 6 % take profit (baseline)
    max_position_size_pct: float = 0.10  # Never > 10 % in one asset


class BacktestConfig(BaseModel):
    start_date: str = "2020-01-01"
    end_date: str = "2024-12-31"
    initial_capital: float = 10_000.0
    commission: float = 0.001            # 0.1 % (Binance maker/taker)
    slippage: float = 0.0005            # 0.05 %


class BotConfig(BaseModel):
    exchange: ExchangeConfig = ExchangeConfig()
    risk: RiskConfig = RiskConfig()
    backtest: BacktestConfig = BacktestConfig()

    # Pairs to trade
    pairs: list[str] = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT",
        "SOL/USDT", "ADA/USDT",
    ]
    timeframe: str = "1h"
    higher_timeframe: str = "4h"   # For trend filter
    dry_run: bool = True

    # Strategy selection
    active_strategy: str = Field(
        default_factory=lambda: os.getenv("ACTIVE_STRATEGY", "regime_adaptive")
    )
    enable_ml: bool = True

    # Telegram
    telegram_token: str = Field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = Field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # API
    api_key: str = Field(default_factory=lambda: os.getenv("API_KEY", "changeme"))
    webhook_secret: str = Field(default_factory=lambda: os.getenv("WEBHOOK_SECRET", "changeme"))

    # Mode
    dry_run: bool = Field(
        default_factory=lambda: os.getenv("DRY_RUN", "true").lower() != "false"
    )

    # Paths
    data_dir: Path = ROOT / "data"
    reports_dir: Path = ROOT / "reports"
    models_dir: Path = ROOT / "models"


CONFIG = BotConfig()
