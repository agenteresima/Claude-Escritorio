#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Claude Trading Bot — Launcher
# Menú principal para controlar el bot sin recordar comandos.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colores ──────────────────────────────────────────────────────────────────
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_DIM='\033[2m'
C_GREEN='\033[0;32m'
C_CYAN='\033[0;36m'
C_YELLOW='\033[0;33m'
C_RED='\033[0;31m'
C_MAGENTA='\033[0;35m'
C_WHITE='\033[0;37m'
C_BG_DARK='\033[48;5;235m'

# ── Activar virtualenv si existe ─────────────────────────────────────────────
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

PYTHON="${PYTHON:-python}"

# ── Helpers ──────────────────────────────────────────────────────────────────
clear_screen() { clear 2>/dev/null || printf '\033[2J\033[H'; }

print_header() {
    clear_screen
    echo -e "${C_CYAN}${C_BOLD}"
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║        📈  CLAUDE TRADING BOT  —  Panel de Control          ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo -e "${C_RESET}"

    # Estado rápido
    local status_color="${C_GREEN}"
    local status_text="✅ ACTIVO"
    if [ -f "data/bot.db" ]; then
        local open_trades
        open_trades=$($PYTHON -c "
from data.database import init_db, get_open_trades; init_db()
trades = get_open_trades()
print(len(trades))
" 2>/dev/null || echo "?")
        echo -e "  ${C_DIM}Posiciones abiertas: ${C_BOLD}${C_YELLOW}${open_trades}${C_RESET}   ${C_DIM}Directorio: ${SCRIPT_DIR}${C_RESET}"
    fi
    echo ""
}

print_menu() {
    echo -e "${C_BOLD}  ── 🤖 ADVISOR ──────────────────────────────────────────────────${C_RESET}"
    echo -e "  ${C_GREEN}[1]${C_RESET} Advisor interactivo       ${C_DIM}(pregunta cualquier cosa al bot)${C_RESET}"
    echo -e "  ${C_GREEN}[2]${C_RESET} Escanear watchlist         ${C_DIM}(¿qué activos entrar ahora?)${C_RESET}"
    echo -e "  ${C_GREEN}[3]${C_RESET} Ver entorno macro           ${C_DIM}(Polymarket: recesión, Fed, inflación)${C_RESET}"
    echo -e "  ${C_GREEN}[4]${C_RESET} Sentimiento de mercado     ${C_DIM}(Fear & Greed + WSB + funding)${C_RESET}"
    echo ""
    echo -e "${C_BOLD}  ── 🔴 TRADING EN VIVO ──────────────────────────────────────────${C_RESET}"
    echo -e "  ${C_YELLOW}[5]${C_RESET} Iniciar bot (paper trading)  ${C_DIM}(DRY_RUN=true, sin dinero real)${C_RESET}"
    echo -e "  ${C_YELLOW}[6]${C_RESET} Iniciar bot (REAL)           ${C_DIM}⚠️  Requiere API key configurada${C_RESET}"
    echo -e "  ${C_YELLOW}[7]${C_RESET} Dashboard Dash               ${C_DIM}(abre en navegador: localhost:8050)${C_RESET}"
    echo -e "  ${C_YELLOW}[8]${C_RESET} API REST (FastAPI)           ${C_DIM}(localhost:8000/docs)${C_RESET}"
    echo ""
    echo -e "${C_BOLD}  ── 📊 ANÁLISIS ─────────────────────────────────────────────────${C_RESET}"
    echo -e "  ${C_CYAN}[9]${C_RESET}  Backtest rápido             ${C_DIM}(estrategia trend_ema, BTC/USDT)${C_RESET}"
    echo -e "  ${C_CYAN}[10]${C_RESET} Comparar estrategias        ${C_DIM}(benchmark todas las estrategias)${C_RESET}"
    echo -e "  ${C_CYAN}[11]${C_RESET} Stats del bot               ${C_DIM}(rendimiento histórico)${C_RESET}"
    echo -e "  ${C_CYAN}[12]${C_RESET} WSB — tickers trending      ${C_DIM}(Reddit WallStreetBets)${C_RESET}"
    echo ""
    echo -e "${C_BOLD}  ── ⚙️  CONFIGURACIÓN ──────────────────────────────────────────${C_RESET}"
    echo -e "  ${C_MAGENTA}[13]${C_RESET} Ver configuración actual    ${C_DIM}(config.yaml + .env)${C_RESET}"
    echo -e "  ${C_MAGENTA}[14]${C_RESET} Backup base de datos        ${C_DIM}(exporta data/bot.db)${C_RESET}"
    echo -e "  ${C_MAGENTA}[15]${C_RESET} Ejecutar tests              ${C_DIM}(pytest suite rápida)${C_RESET}"
    echo ""
    echo -e "  ${C_RED}[0]${C_RESET}  Salir"
    echo ""
    echo -ne "  ${C_BOLD}Elige una opción:${C_RESET} "
}

press_enter() {
    echo ""
    echo -e "  ${C_DIM}Pulsa Enter para volver al menú...${C_RESET}"
    read -r
}

ask_watchlist() {
    echo -e "\n  ${C_BOLD}Introduce los activos separados por espacio:${C_RESET}"
    echo -e "  ${C_DIM}Ejemplos: BTC/USDT ETH/USDT SOL/USDT   o   NVDA TSLA AAPL${C_RESET}"
    echo -ne "  > "
    read -r wl_input
    if [ -z "$wl_input" ]; then
        wl_input="BTC/USDT ETH/USDT SOL/USDT"
    fi
    # Construye args -w para cada activo
    local wl_args=""
    for sym in $wl_input; do
        wl_args="$wl_args -w $sym"
    done
    echo ""
    $PYTHON main.py advisor $wl_args
}

ask_question() {
    echo -e "\n  ${C_BOLD}¿Qué quieres preguntar?${C_RESET}"
    echo -e "  ${C_DIM}Ejemplos:${C_RESET}"
    echo -e "  ${C_DIM}  · ¿BTC/USDT pasa todos los filtros para invertir ahora?${C_RESET}"
    echo -e "  ${C_DIM}  · ¿Cuál es el riesgo macro actual?${C_RESET}"
    echo -e "  ${C_DIM}  · ¿Qué señal tiene NVDA?${C_RESET}"
    echo ""
    echo -ne "  > "
    read -r question
    if [ -n "$question" ]; then
        echo ""
        $PYTHON main.py ask "$question"
    fi
}

run_backtest() {
    echo -e "\n  ${C_BOLD}Par a testear (Enter = BTC/USDT):${C_RESET} "
    echo -ne "  > "
    read -r pair
    pair="${pair:-BTC/USDT}"
    echo ""
    $PYTHON main.py backtest --strategy trend_ema --pair "$pair"
}

show_config() {
    echo ""
    echo -e "${C_BOLD}  ── config.yaml ─────────────────────────────────────────────${C_RESET}"
    if [ -f "config/config.yaml" ]; then
        cat config/config.yaml | head -40
    else
        echo "  No encontrado: config/config.yaml"
    fi
    echo ""
    echo -e "${C_BOLD}  ── .env ────────────────────────────────────────────────────${C_RESET}"
    if [ -f ".env" ]; then
        # Muestra variables sin exponer secretos
        grep -v "SECRET\|PASSWORD\|API_KEY" .env 2>/dev/null || echo "  (variables sensibles ocultas)"
    else
        echo "  .env no encontrado — copia .env.example como .env"
    fi
}

# ── Main loop ────────────────────────────────────────────────────────────────
main() {
    while true; do
        print_header
        print_menu
        read -r choice

        case "$choice" in
            1)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  🤖 Advisor interactivo — escribe 'exit' para volver al menú${C_RESET}\n"
                $PYTHON main.py advisor || true
                ;;
            2)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📊 Escaneo de watchlist${C_RESET}"
                ask_watchlist
                press_enter
                ;;
            3)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  🌍 Entorno macro — Polymarket${C_RESET}\n"
                $PYTHON main.py ask "Dame un resumen completo del entorno macro actual: Polymarket, Fed, recesión, inflación. ¿Debo estar largo o cauteloso?"
                press_enter
                ;;
            4)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📈 Sentimiento de mercado${C_RESET}\n"
                $PYTHON main.py polymarket
                echo ""
                $PYTHON main.py wsb
                press_enter
                ;;
            5)
                clear_screen
                echo -e "${C_YELLOW}${C_BOLD}  🟡 Paper Trading (DRY_RUN=true) — Ctrl+C para parar${C_RESET}\n"
                DRY_RUN=true $PYTHON main.py live --dry-run || true
                press_enter
                ;;
            6)
                clear_screen
                echo -e "${C_RED}${C_BOLD}  ⚠️  Trading REAL — asegúrate de tener configurado el .env${C_RESET}"
                echo -e "  ${C_DIM}Pulsa Enter para continuar o Ctrl+C para cancelar...${C_RESET}"
                read -r
                $PYTHON main.py live || true
                press_enter
                ;;
            7)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📊 Iniciando Dashboard (http://localhost:8050)${C_RESET}\n"
                $PYTHON main.py dashboard &
                sleep 2
                # Intentar abrir navegador
                xdg-open "http://localhost:8050" 2>/dev/null \
                    || open "http://localhost:8050" 2>/dev/null \
                    || echo "  Abre http://localhost:8050 en tu navegador"
                press_enter
                ;;
            8)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  🔌 Iniciando API REST (http://localhost:8000/docs)${C_RESET}\n"
                $PYTHON main.py api &
                sleep 2
                xdg-open "http://localhost:8000/docs" 2>/dev/null \
                    || open "http://localhost:8000/docs" 2>/dev/null \
                    || echo "  Abre http://localhost:8000/docs en tu navegador"
                press_enter
                ;;
            9)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📉 Backtest${C_RESET}\n"
                run_backtest
                press_enter
                ;;
            10)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📊 Comparar estrategias${C_RESET}\n"
                $PYTHON main.py compare --pair BTC/USDT || true
                press_enter
                ;;
            11)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  📈 Estadísticas del bot${C_RESET}\n"
                $PYTHON main.py stats || true
                press_enter
                ;;
            12)
                clear_screen
                echo -e "${C_CYAN}${C_BOLD}  💬 Reddit WallStreetBets — Tickers trending${C_RESET}\n"
                $PYTHON main.py wsb --top 30 || true
                press_enter
                ;;
            13)
                clear_screen
                echo -e "${C_MAGENTA}${C_BOLD}  ⚙️  Configuración${C_RESET}"
                show_config
                press_enter
                ;;
            14)
                clear_screen
                echo -e "${C_MAGENTA}${C_BOLD}  💾 Backup de base de datos${C_RESET}\n"
                $PYTHON main.py backup --tag "manual_$(date +%Y%m%d_%H%M)" || true
                press_enter
                ;;
            15)
                clear_screen
                echo -e "${C_MAGENTA}${C_BOLD}  🧪 Tests rápidos${C_RESET}\n"
                python -m pytest tests/ -x -q --tb=short --ignore=tests/test_ml.py 2>&1 | tail -30 || true
                press_enter
                ;;
            0|q|Q|exit|salir)
                clear_screen
                echo -e "\n  ${C_CYAN}${C_BOLD}Hasta luego. 📈${C_RESET}\n"
                exit 0
                ;;
            *)
                echo -e "\n  ${C_RED}Opción no válida.${C_RESET}"
                sleep 1
                ;;
        esac
    done
}

# Si se pasa un argumento directo, ejecutar sin menú
case "${1:-}" in
    advisor)  shift; exec $PYTHON main.py advisor "$@" ;;
    ask)      shift; exec $PYTHON main.py ask "$@" ;;
    live)     shift; exec $PYTHON main.py live "$@" ;;
    backtest) shift; exec $PYTHON main.py backtest "$@" ;;
    *)        main ;;
esac
