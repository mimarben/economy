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
```


