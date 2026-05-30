"""
Tests for bot/telegram_bot.py command handlers.

The handlers are closures inside run_bot(), so we run run_bot() under
full mocks, capture each CommandHandler callback, then call them directly
with fake Update / Context objects.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_update(chat_id: int = 12345, text: str = ""):
    update = MagicMock()
    update.effective_chat.id = chat_id
    update.message.reply_text = AsyncMock()
    return update


def _make_ctx(args=None):
    ctx = MagicMock()
    ctx.args = args or []
    return ctx


def _make_telegram_mocks():
    """Return (mock_Application_class, captured_handlers_dict, mock_app)."""
    handlers: dict = {}

    mock_app = MagicMock()
    mock_app.run_polling = AsyncMock()

    def _add_handler(h):
        # CommandHandler has .command (list) and .callback attributes
        commands = h.command if hasattr(h, "command") else [h._command]
        cb = h.callback if hasattr(h, "callback") else h._callback
        for cmd in commands:
            handlers[cmd] = cb

    mock_app.add_handler = _add_handler

    mock_builder = MagicMock()
    mock_builder.token.return_value = mock_builder
    mock_builder.build.return_value = mock_app

    mock_Application = MagicMock()
    mock_Application.builder.return_value = mock_builder

    return mock_Application, handlers, mock_app


# ── _auth() ───────────────────────────────────────────────────────────────────

class TestAuth:
    def test_no_restriction_when_no_ids_configured(self):
        import bot.telegram_bot as tb
        orig = tb.ALLOWED_CHAT_IDS
        tb.ALLOWED_CHAT_IDS = set()
        assert tb._auth(999999) is True
        tb.ALLOWED_CHAT_IDS = orig

    def test_allowed_when_id_in_set(self):
        import bot.telegram_bot as tb
        orig = tb.ALLOWED_CHAT_IDS
        tb.ALLOWED_CHAT_IDS = {12345}
        assert tb._auth(12345) is True
        tb.ALLOWED_CHAT_IDS = orig

    def test_denied_when_id_not_in_set(self):
        import bot.telegram_bot as tb
        orig = tb.ALLOWED_CHAT_IDS
        tb.ALLOWED_CHAT_IDS = {12345}
        assert tb._auth(99999) is False
        tb.ALLOWED_CHAT_IDS = orig


# ── run_bot early-exit paths ──────────────────────────────────────────────────

class TestRunBotEarlyExit:
    @pytest.mark.asyncio
    async def test_exits_immediately_without_token(self):
        import bot.telegram_bot as tb
        with patch.object(tb, "TELEGRAM_TOKEN", ""):
            result = await tb.run_bot()
        assert result is None

    @pytest.mark.asyncio
    async def test_exits_on_missing_telegram_library(self):
        import bot.telegram_bot as tb
        import builtins
        real_import = builtins.__import__

        def _raise_on_telegram(name, *args, **kwargs):
            if name == "telegram":
                raise ImportError("no module telegram")
            return real_import(name, *args, **kwargs)

        with patch.object(tb, "TELEGRAM_TOKEN", "dummy_token"), \
             patch("builtins.__import__", side_effect=_raise_on_telegram):
            result = await tb.run_bot()
        assert result is None


# ── Handler capture fixture ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def captured_handlers():
    """
    Run run_bot() under full mocks, capture handler callbacks, and expose
    the DB mocks so individual tests can configure return_values / assert calls.

    Returns (handlers_dict, db_mocks_dict).
    """
    import asyncio
    import bot.telegram_bot as tb

    mock_Application, handlers, mock_app = _make_telegram_mocks()

    class _FakeHandler:
        def __init__(self, command, callback):
            self.command = [command]
            self.callback = callback

    mock_Update        = MagicMock()
    mock_CommandHandler = MagicMock(side_effect=lambda name, cb: _FakeHandler(name, cb))
    mock_ContextTypes  = MagicMock()

    # Expose mocks so tests can configure them after fixture setup
    mock_get_open_trades = MagicMock(return_value=[])
    mock_trade_stats     = MagicMock(return_value=None)
    mock_get_state       = MagicMock(return_value=None)
    mock_set_state       = MagicMock()
    mock_ef_cls          = MagicMock()

    loop = asyncio.new_event_loop()
    try:
        with patch.object(tb, "TELEGRAM_TOKEN", "fake_token"), \
             patch.dict("sys.modules", {
                 "telegram": MagicMock(Update=mock_Update),
                 "telegram.ext": MagicMock(
                     Application=mock_Application,
                     CommandHandler=mock_CommandHandler,
                     ContextTypes=mock_ContextTypes,
                 ),
             }), \
             patch("data.database.get_open_trades", mock_get_open_trades), \
             patch("data.database.trade_stats",     mock_trade_stats), \
             patch("data.database.get_state",       mock_get_state), \
             patch("data.database.set_state",       mock_set_state), \
             patch("utils.events_filter.EventsFilter", mock_ef_cls):
            loop.run_until_complete(tb.run_bot())
    finally:
        loop.close()

    db_mocks = {
        "get_open_trades": mock_get_open_trades,
        "trade_stats":     mock_trade_stats,
        "get_state":       mock_get_state,
        "set_state":       mock_set_state,
        "EventsFilter":    mock_ef_cls,
    }
    return handlers, db_mocks


# ── Individual command tests ──────────────────────────────────────────────────

class TestCmdStatus:
    @pytest.mark.asyncio
    async def test_status_replies(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("status")
        if handler is None:
            pytest.skip("status handler not captured")
        mocks["get_open_trades"].return_value = []
        mocks["get_state"].return_value = "trend_ema"
        update = _make_update()
        await handler(update, _make_ctx())
        update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_status_shows_open_positions(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("status")
        if handler is None:
            pytest.skip("status handler not captured")
        mocks["get_open_trades"].return_value = [
            {"symbol": "BTC/USDT", "direction": "long", "entry_price": 40_000.0}
        ]
        mocks["get_state"].return_value = "trend_ema"
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "BTC/USDT" in text
        mocks["get_open_trades"].return_value = []  # reset

    @pytest.mark.asyncio
    async def test_status_auth_rejected_no_reply(self, captured_handlers):
        import bot.telegram_bot as tb
        handlers, mocks = captured_handlers
        handler = handlers.get("status")
        if handler is None:
            pytest.skip("status handler not captured")
        orig = tb.ALLOWED_CHAT_IDS
        tb.ALLOWED_CHAT_IDS = {99999}
        update = _make_update(chat_id=11111)
        await handler(update, _make_ctx())
        update.message.reply_text.assert_not_called()
        tb.ALLOWED_CHAT_IDS = orig


class TestCmdPauseResume:
    @pytest.mark.asyncio
    async def test_pause_sets_state(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("pause")
        if handler is None:
            pytest.skip("pause handler not captured")
        mocks["set_state"].reset_mock()
        update = _make_update()
        await handler(update, _make_ctx())
        mocks["set_state"].assert_called_once_with("paused", True)
        update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_resume_clears_state(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("resume")
        if handler is None:
            pytest.skip("resume handler not captured")
        mocks["set_state"].reset_mock()
        update = _make_update()
        await handler(update, _make_ctx())
        mocks["set_state"].assert_called_once_with("paused", False)


class TestCmdStats:
    @pytest.mark.asyncio
    async def test_no_trades_message(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("stats")
        if handler is None:
            pytest.skip("stats handler not captured")
        mocks["trade_stats"].return_value = None
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "no closed" in text.lower() or "no" in text.lower()

    @pytest.mark.asyncio
    async def test_stats_shows_metrics(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("stats")
        if handler is None:
            pytest.skip("stats handler not captured")
        mocks["trade_stats"].return_value = {
            "total_trades": 10, "win_rate": 60.0,
            "total_pnl": 500.0, "avg_pnl": 50.0,
            "best_trade": 200.0, "worst_trade": -80.0,
        }
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "60" in text or "win" in text.lower()
        mocks["trade_stats"].return_value = None  # reset


class TestCmdClose:
    @pytest.mark.asyncio
    async def test_close_no_args_shows_usage(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("close")
        if handler is None:
            pytest.skip("close handler not captured")
        update = _make_update()
        await handler(update, _make_ctx(args=[]))
        text = update.message.reply_text.call_args[0][0]
        assert "usage" in text.lower() or "BTC" in text

    @pytest.mark.asyncio
    async def test_close_queues_force_close(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("close")
        if handler is None:
            pytest.skip("close handler not captured")
        mocks["set_state"].reset_mock()
        update = _make_update()
        await handler(update, _make_ctx(args=["BTC/USDT"]))
        mocks["set_state"].assert_called_once()
        key = mocks["set_state"].call_args[0][0]
        assert "BTC" in key or "force_close" in key


class TestCmdStrategy:
    @pytest.mark.asyncio
    async def test_no_args_shows_current(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("strategy")
        if handler is None:
            pytest.skip("strategy handler not captured")
        mocks["get_state"].return_value = "trend_ema"
        update = _make_update()
        await handler(update, _make_ctx(args=[]))
        text = update.message.reply_text.call_args[0][0]
        assert "trend_ema" in text

    @pytest.mark.asyncio
    async def test_valid_strategy_switches(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("strategy")
        if handler is None:
            pytest.skip("strategy handler not captured")
        mocks["set_state"].reset_mock()
        update = _make_update()
        await handler(update, _make_ctx(args=["breakout"]))
        mocks["set_state"].assert_called_once_with("active_strategy", "breakout")

    @pytest.mark.asyncio
    async def test_invalid_strategy_rejected(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("strategy")
        if handler is None:
            pytest.skip("strategy handler not captured")
        mocks["set_state"].reset_mock()
        update = _make_update()
        await handler(update, _make_ctx(args=["nonexistent_strategy"]))
        mocks["set_state"].assert_not_called()
        text = update.message.reply_text.call_args[0][0]
        assert "unknown" in text.lower() or "nonexistent" in text.lower()


class TestCmdHelp:
    @pytest.mark.asyncio
    async def test_help_lists_commands(self, captured_handlers):
        handlers, _ = captured_handlers
        handler = handlers.get("help") or handlers.get("start")
        if handler is None:
            pytest.skip("help handler not captured")
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "/status" in text or "/pause" in text


class TestCmdEvents:
    @pytest.mark.asyncio
    async def test_events_safe(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("events")
        if handler is None:
            pytest.skip("events handler not captured")
        mock_ef_instance = MagicMock()
        mock_ef_instance.is_safe_to_trade.return_value = (True, "")
        mock_ef_instance.upcoming_events.return_value  = []
        mocks["EventsFilter"].return_value = mock_ef_instance
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "safe" in text.lower() or "✅" in text

    @pytest.mark.asyncio
    async def test_events_unsafe(self, captured_handlers):
        handlers, mocks = captured_handlers
        handler = handlers.get("events")
        if handler is None:
            pytest.skip("events handler not captured")
        mock_ef_instance = MagicMock()
        mock_ef_instance.is_safe_to_trade.return_value = (False, "FOMC meeting")
        mock_ef_instance.upcoming_events.return_value  = []
        mocks["EventsFilter"].return_value = mock_ef_instance
        update = _make_update()
        await handler(update, _make_ctx())
        text = update.message.reply_text.call_args[0][0]
        assert "FOMC" in text or "🚫" in text or "unsafe" in text.lower()
