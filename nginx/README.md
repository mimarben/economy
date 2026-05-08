Flujo correcto completo
1. Instalar mkcert
  `sudo dnf install mkcert nss-tools`

2. Cerrar apps que bloquean NSS
  MUY importante en Fedora + Chromium + Flatpak.
  `pkill chrome`
  `pkill chromium`
  `pkill code`
  **Surfshark:**
  flatpak ps

  flatpak kill com.surfshark.Surfshark
  Verificar:
  `lsof | grep nssdb`
  Debe no devolver nada.

3. Resetear NSS DB (solo si está corrupta)
rm -rf ~/.pki/nssdb

4. Reinstalar CA mkcert
mkcert -uninstallmkcert -install

5. Verificar CA instalada
certutil -L -d sql:$HOME/.pki/nssdb
Debe aparecer algo parecido a:
mkcert development CA

6. Configurar hosts
sudo nano /etc/hosts
Añadir:
127.0.0.1 economy.app.local
Verificar:
ping economy.app.local
Debe resolver a:
127.0.0.1

7. Crear certificados CORRECTOS
NO usar openssl.
Eliminar certificados viejos:
rm -f nginx/certs/*.pem
Generar:
mkdir -p nginx/certsmkcert \  -key-file nginx/certs/economy.app.local-key.pem \  -cert-file nginx/certs/economy.app.local.pem \  economy.app.local localhost 127.0.0.1

8. Verificar certificado generado
MUY importante:
openssl x509 -in nginx/certs/economy.app.local.pem -text -noout
Buscar:
Issuer:
Debe ser:
mkcert development CA
NO:
CN=economy.app.local

9. Verificar Nginx DENTRO del contenedor
  Muy importante.
  docker exec -it economy_nginx nginx -t
  Luego:
  docker exec -it economy_nginx ls -l /etc/nginx/certs
  Verifica que:


existen los PEM


fechas correctas



11. Verificar qué certificado sirve realmente Nginx
ESTE es el paso clave.
openssl s_client \  -connect economy.app.local:443 \  -servername economy.app.local
Busca:
issuer=
Debe salir:
mkcert development CA

Si sigue saliendo self-signed
Entonces Nginx sirve otro PEM.
Posibles causas:
A. Docker COPY viejo
En Dockerfile:
COPY nginx/certs /etc/nginx/certs
pero la imagen no se rebuildó.
Haz:
docker compose down -vdocker compose build --no-cachedocker compose up

B. Volumen pisa certificados
Ejemplo:
volumes:  - ./nginx:/etc/nginx
y dentro hay PEM antiguos.

C. Estás entrando por localhost
Si el certificado es:
economy.app.local
pero visitas:
https://localhost
Chrome dirá inválido.

D. HSTS cacheado
Chromium cachea agresivamente.
Limpiar:
chrome://net-internals/#hsts
Delete domain security policies:
economy.app.local

Sobre Surfshark
Sí, Surfshark rompe bastantes veces:


NSS DB


trust store


DNS local


certificados locales


Especialmente Flatpak.
Cuando falle:
flatpak kill com.surfshark.Surfshark
y reiniciar Chromium suele arreglarlo.

NO uses esto
Elimínalo completamente del manual:
openssl req -x509 ...
Eso genera self-signed y rompe todo el flujo.

Arquitectura recomendada final
Frontend
Angular compilado:
ng build --configuration production
Nginx sirve /dist.

Reverse proxy
Nginx:


SSL mkcert


rate limit


gzip


websocket proxy


load balancing



Docker
docker-compose.ymldocker-compose.override.yml
override para:


bind mounts


hot reload


debug



Tu problema REAL ahora mismo
Por la captura:
✅ mkcert funciona
✅ CA instalada
✅ Chromium reconoce CA
Así que el error viene de:

Nginx sigue sirviendo un certificado viejo/autofirmado.

El comando decisivo es:
openssl s_client \  -connect economy.app.local:443 \  -servername economy.app.local
Ahí se verá inmediatamente qué certificado sale realmente.****