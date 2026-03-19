#? Execution: ./restore_postgres.sh /mnt/src/dev/economy/backups/economy_2026-03-19_18-30.dump

#!/bin/bash

BACKUP_DIR="/mnt/src/dev/economy/backups"
DB_NAME="economy"
CONTAINER="economy_db"

# Si pasas archivo como argumento lo usa, si no usa el último
if [ -n "$1" ]; then
  BACKUP_FILE="$1"
else
  BACKUP_FILE=$(ls -t $BACKUP_DIR/*.dump 2>/dev/null | head -n 1)
fi

if [ -z "$BACKUP_FILE" ]; then
  echo "❌ No se encontró ningún backup"
  exit 1
fi

echo "📦 Usando backup: $BACKUP_FILE"

# Confirmación (evita cagadas)
read -p "⚠️ Esto borrará la base de datos '$DB_NAME'. ¿Continuar? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "❌ Cancelado"
  exit 1
fi

# Drop + create DB
echo "🗑️ Eliminando base de datos..."
docker exec -i $CONTAINER dropdb -U postgres --if-exists $DB_NAME

echo "🆕 Creando base de datos..."
docker exec -i $CONTAINER createdb -U postgres $DB_NAME

# Restore
echo "♻️ Restaurando..."
cat "$BACKUP_FILE" | docker exec -i $CONTAINER pg_restore -U postgres -d $DB_NAME

echo "✅ Restore completado"