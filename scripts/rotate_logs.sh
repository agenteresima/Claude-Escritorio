#!/usr/bin/env bash
# Rotate logs and backups — run daily via cron
# Example cron: 0 2 * * * /app/scripts/rotate_logs.sh >> /app/logs/cron.log 2>&1

LOGS_DIR=${LOGS_DIR:-./logs}
BACKUPS_DIR=${BACKUPS_DIR:-./data/backups}
KEEP_LOGS=30
KEEP_BACKUPS=30

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Running maintenance..."

# Remove old logs
if [ -d "$LOGS_DIR" ]; then
    find "$LOGS_DIR" -name "*.log.*" -mtime +${KEEP_LOGS} -delete
    echo "  Logs older than ${KEEP_LOGS} days removed."
fi

# Remove old backups (Python backup.py already prunes, this is belt-and-suspenders)
if [ -d "$BACKUPS_DIR" ]; then
    backup_count=$(ls "$BACKUPS_DIR"/bot_*.db 2>/dev/null | wc -l)
    if [ "$backup_count" -gt "$KEEP_BACKUPS" ]; then
        ls -t "$BACKUPS_DIR"/bot_*.db | tail -n +$((KEEP_BACKUPS + 1)) | xargs rm -f
        echo "  Pruned old backups, kept last ${KEEP_BACKUPS}."
    fi
fi

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Maintenance complete."
