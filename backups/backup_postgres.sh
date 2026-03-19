#!/bin/bash

BACKUP_DIR="/mnt/src/dev/economy/backups"
DB_NAME="economy"
CONTAINER="economy_db"
DATE=$(date +%F_%H-%M)

mkdir -p $BACKUP_DIR

docker exec -t $CONTAINER \
  pg_dump -U postgres -d $DB_NAME -Fc \
  > $BACKUP_DIR/${DB_NAME}_$DATE.dump

# borrar backups de más de 7 días
find $BACKUP_DIR -type f -mtime +7 -delete