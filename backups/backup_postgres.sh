#!/bin/bash

BACKUP_DIR="/mnt/SRC/dev/economy/backups"
DB_NAME="economy"
DB_USER="miguel"
CONTAINER="economy_db"
DATE=$(date +%F_%H-%M)

mkdir -p $BACKUP_DIR

docker exec -t $CONTAINER \
  pg_dump -U $DB_USER -d $DB_NAME -Fc \
  > $BACKUP_DIR/${DB_NAME}_$DATE.dump

# borrar backups de más de 7 días
find $BACKUP_DIR -type f -name "*.dump" -mtime +7 -delete