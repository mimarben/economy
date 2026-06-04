# Copia de respaldo de la base de datos

``` bash
./backup_postgres.sh
```

# Restauracion de la base de datos

``` bash
./restore_postgres.sh /mnt/src/dev/economy/backups/economy_2026-03-19_18-30.dump
```

# .gitignore

``` yaml
/backups/*
!/backups/README.md
!/backups/backup_postgres.sh
!/backups/restore_postgres.sh



Bash Run backup script and verify output
IN
chmod +x /mnt/SRC/dev/economy/backups/backup_postgres.sh && chmod +x /mnt/SRC/dev/economy/backups/restore_postgres.sh && /mnt/SRC/dev/economy/backups/backup_postgres.sh && ls -lh /mnt/SRC/dev/economy/backups/*.dump

OUT
Permissions Size User   Date Modified Name
.rw-r--r--@  89k miguel  4 Jun 08:51  /mnt/SRC/dev/economy/backups/economy_2026-06-04_08-51.dump
Funciona. Ahora configura el cron:


crontab -e
Añade:


0 3 * * * /mnt/SRC/dev/economy/backups/backup_postgres.sh >> /mnt/SRC/dev/economy/logs/backup.log 2>&1
```


