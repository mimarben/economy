# Nginx Reverse Proxy

- Servir Angular ya compilado desde Nginx (más limpio) 
- Meter HTTPS local con mkcert 
- Añadir rate limiting en /ai 
- Meter load balancing para backend 
-Separar entorno dev/prod con docker-compose.override.yml


# Certificates

sudo dnf install mkcert nss-tools

sudo mkcert -install

mkcert economy.app.local



Luego tocar etc/hosts y poner 127.0.0.1 economy.app.local

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout economy.app.local-key.pem \
  -out economy.app.local.pem \
  -days 365 \
  -subj "/CN=economy.app.local"

este certificado no es CA trust es mejor con mkcert (parece que se pega con sufrsark)

Comprobar ngnix config:
  
docker exec -it economy_nginx nginx -t
       
Luego Traefik

mkcert da problemas con surfshark


para todo
flatpak kill --all



Quien usa esto: necesrio apra que no se quede bloqueado
lsof | grep nssdb                                                                                                                                                            ✔ ╱ 9s  


# 1️⃣ Cerrar completamente Chrome
pkill chrome

# 1️⃣ Cerrar completamente Vscode
pkill code
# 1️⃣ Cerrar completamente surfshark
flatpak ps
flatpak kill com.surfshark.Surfshark

# (Opcional) verificar que no queda ningún proceso
ps aux | grep chrome

# 2️⃣ Verificar que NSS ya no está bloqueado
lsof | grep nssdb

# Debe NO devolver nada

# 3️⃣ Eliminar base NSS del usuario (se regenera sola)
rm -rf ~/.pki/nssdb

# 4️⃣ Reinstalar CA local mkcert
mkcert -uninstall
mkcert -install

# 5️⃣ Ir a la raíz del proyecto
cd /home/miguel/src/economy

# 6️⃣ Crear carpeta certs si no existe
mkdir -p nginx/certs

# 7 Crear los certifcados
mkcert -key-file nginx/certs/economy.app.local-key.pem \
       -cert-file nginx/certs/economy.app.local.pem \
       economy.app.local
       

# 7️⃣ Generar certificado válido para dominio + localhost
mkcert -key-file nginx/certs/economy.app.local-key.pem \
       -cert-file nginx/certs/economy.app.local.pem \
       economy.app.local localhost 127.0.0.1

# 8️⃣ Verificar que se generaron los archivos
ls -l nginx/certs

# 9️⃣ Reiniciar contenedores
docker compose down
docker compose up --build


------------------
