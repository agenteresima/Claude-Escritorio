#!/usr/bin/env bash
# One-command setup for the Professional Trading Bot
# Usage: bash install.sh

set -euo pipefail

YELLOW='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${YELLOW}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
err()   { echo -e "${RED}[ERR]${NC}  $1"; exit 1; }

echo ""
echo "  ╔════════════════════════════════════╗"
echo "  ║  Professional Trading Bot Setup    ║"
echo "  ╚════════════════════════════════════╝"
echo ""

# ── Python version check ─────────────────────────────────────────────────────
info "Checking Python version..."
PYTHON=$(which python3 || which python || err "Python not found")
PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
    ok "Python $PY_VER found"
else
    err "Python 3.10+ required (found $PY_VER)"
fi

# ── Virtual environment ───────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv .venv
    ok "Virtual environment created at .venv/"
else
    ok "Virtual environment already exists"
fi

source .venv/bin/activate

# ── TA-Lib C library (optional) ───────────────────────────────────────────────
if ! python -c "import talib" 2>/dev/null; then
    info "TA-Lib not found — attempting system install..."
    if command -v apt-get &>/dev/null; then
        apt-get install -y libta-lib-dev 2>/dev/null || true
    elif command -v brew &>/dev/null; then
        brew install ta-lib 2>/dev/null || true
    fi
fi

# ── Python dependencies ───────────────────────────────────────────────────────
info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
ok "Dependencies installed"

# ── Environment file ──────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    info "Creating .env from example..."
    cp .env.example .env
    ok ".env created — edit it with your API keys"
else
    ok ".env already exists"
fi

# ── Directory structure ───────────────────────────────────────────────────────
info "Creating directories..."
mkdir -p data/cache data/backups models reports logs
ok "Directories ready"

# ── Run tests ─────────────────────────────────────────────────────────────────
info "Running quick sanity tests..."
python -m pytest tests/ -q --tb=short -x 2>&1 | tail -5 || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup complete! Next steps:           ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  1. Edit .env with your API keys        ║${NC}"
echo -e "${GREEN}║  2. make backtest  (test a strategy)    ║${NC}"
echo -e "${GREEN}║  3. make compare   (rank all strategies)║${NC}"
echo -e "${GREEN}║  4. make live      (paper trade)        ║${NC}"
echo -e "${GREEN}║  5. make dashboard (open browser)       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "  Activate env:  source .venv/bin/activate"
echo "  Full help:     make help"
echo ""
