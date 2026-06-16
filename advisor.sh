#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Asesor de Inversión IA — acceso directo
#  Lanza el advisor conversacional del trading bot.
# ─────────────────────────────────────────────────────────────
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_DIR"

# Activar entorno virtual si existe
[ -f ".venv/bin/activate" ] && source .venv/bin/activate
[ -f "venv/bin/activate"  ] && source venv/bin/activate

clear
printf '\033[0;36m\033[1m'
printf '  ┌─────────────────────────────────────────────────────────┐\n'
printf '  │      🤖  Asesor de Inversión IA — en línea              │\n'
printf '  │  Pregúntame qué acciones entrar, el entorno macro,      │\n'
printf '  │  si un activo pasa los filtros, o cualquier duda.        │\n'
printf '  │  Escribe "exit" para salir.                              │\n'
printf '  └─────────────────────────────────────────────────────────┘\n'
printf '\033[0m\n'

exec python main.py advisor "$@"
