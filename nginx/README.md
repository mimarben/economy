# SSL local para economy.local.app

Este documento explica cómo configurar HTTPS local con certificado confiable
usando **mkcert** para que los navegadores no muestren errores de seguridad.

**Dominio correcto: `economy.local.app`**

---

## Resumen rápido (si ya falló antes)

```bash
# 1. Generar certificado
mkcert \
  -key-file nginx/certs/economy.local.app-key.pem \
  -cert-file nginx/certs/economy.local.app.pem \
  economy.local.app localhost 127.0.0.1

# 2. Añadir al /etc/hosts
echo "127.0.0.1 economy.local.app" | sudo tee -a /etc/hosts

# 3. Reconstruir contenedores
docker compose down
docker compose up -d

# 4. Abrir
# https://economy.local.app/
```

---

## Guía completa paso a paso

### 1. Instalar mkcert

mkcert crea certificados firmados por una CA local que tu navegador reconoce
como válida. **Nunca uses `openssl req -x509 ...`**, eso genera certificados
autofirmados que el navegador siempre rechazará.

**Fedora/RHEL:**
```bash
sudo dnf install mkcert nss-tools
```

**Ubuntu/Debian:**
```bash
sudo apt install mkcert libnss3-tools
```

**Arch:**
```bash
sudo pacman -S mkcert nss
```

Verificar instalación:
```bash
mkcert -version
```

### 2. Cerrar aplicaciones que bloquean NSS

Las bases de datos NSS (Network Security Services) son donde Chrome/Chromium
guardan los certificados de confianza. Si alguna app las tiene abiertas,
mkcert no puede instalar la CA.

**Esto es especialmente importante en Fedora + Chromium/Chrome Flatpak.**

```bash
pkill chrome
pkill chromium
pkill code
```

**Si usas Surfshark (Flatpak):**
```bash
flatpak kill com.surfshark.Surfshark
```

Verificar que nada bloquea NSS:
```bash
lsof | grep nssdb
```
**No debe devolver nada.** Si devuelve algo, cierra esas aplicaciones.

### 3. Instalar la CA raíz de mkcert

Esto registra la CA de mkcert en el sistema y en los navegadores (Chrome,
Chromium, Firefox) como una autoridad certificadora de confianza.

```bash
mkcert -install
```

Si la CA ya estaba instalada y hay problemas, resetear:
```bash
mkcert -uninstall
mkcert -install
```

Verificar que la CA está instalada:
```bash
certutil -L -d sql:$HOME/.pki/nssdb
```
Debe aparecer una línea con `mkcert development CA`.

**Si la base NSS está corrupta:**
```bash
rm -rf ~/.pki/nssdb
mkcert -install
```

### 4. Configurar /etc/hosts

El navegador necesita resolver `economy.local.app` a `127.0.0.1`.

```bash
sudo nano /etc/hosts
```

Añadir esta línea (o verificar que ya existe):
```
127.0.0.1 economy.local.app
```

Verificar:
```bash
ping -c 1 economy.local.app
```
Debe responder desde `127.0.0.1`.

### 5. Generar los certificados

**Importante:** el certificado debe incluir todos los nombres por los que
se va a acceder. Aquí incluimos `economy.local.app`, `localhost` y `127.0.0.1`.

```bash
cd /ruta/al/proyecto/economy

# Eliminar certificados viejos si existen
rm -f nginx/certs/economy.local.app*.pem

# Crear directorio si no existe
mkdir -p nginx/certs

# Generar certificado
mkcert \
  -key-file nginx/certs/economy.local.app-key.pem \
  -cert-file nginx/certs/economy.local.app.pem \
  economy.local.app localhost 127.0.0.1
```

Resultado esperado:
```
Created a new certificate valid for the following names 📜
 - "economy.local.app"
 - "localhost"
 - "127.0.0.1"
```

### 6. Verificar el certificado generado

```bash
openssl x509 -in nginx/certs/economy.local.app.pem -text -noout
```

Buscar estos campos:
- **Issuer:** debe decir `mkcert development CA` (NO `CN=economy.local.app`)
- **Subject Alternative Name:** debe incluir `economy.local.app`, `localhost`, `127.0.0.1`

Si el Issuer NO es mkcert, el certificado es autofirmado y los navegadores
lo rechazarán. Vuelve al paso 3 y regenera.

### 7. Levantar los contenedores

Nginx se configura automáticamente con los archivos en `nginx/nginx.conf`
y `nginx/certs/` mediante volúmenes de Docker (ver `docker-compose.yml`).

```bash
docker compose down
docker compose up -d
```

Si la imagen de nginx se construye con `COPY` de certificados en el
Dockerfile (no es el caso aquí, se usan volúmenes), hay que reconstruir:
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### 8. Verificar que Nginx sirve el certificado correcto

**Este es el paso clave para diagnosticar problemas:**

```bash
openssl s_client \
  -connect economy.local.app:443 \
  -servername economy.local.app 2>/dev/null \
  | openssl x509 -noout -issuer -subject
```

Resultado correcto:
```
issuer=O=mkcert development CA, OU=..., CN=mkcert ...
subject=O=mkcert development certificate, OU=...
```

Si aparece `issuer=CN=economy.local.app` o similar, Nginx está sirviendo
un certificado autofirmado. Ver la sección de problemas abajo.

### 9. Verificar dentro del contenedor

```bash
# Test de configuración
docker exec -it economy_nginx nginx -t

# Ver que los certificados están montados
docker exec -it economy_nginx ls -la /etc/nginx/certs/
```

Deben existir:
- `economy.local.app.pem`
- `economy.local.app-key.pem`

---

## Solución de problemas

### ERR_CERT_COMMON_NAME_INVALID

**Causa:** estás accediendo por un nombre que no está en el certificado.

- El dominio correcto es **`economy.local.app`** (no `economy.app.local`,
  ni `localhost` con un certificado solo para `economy.local.app`, etc.)
- Verifica qué nombres cubre el certificado:
  ```bash
  openssl x509 -in nginx/certs/economy.local.app.pem -text -noout | grep -A1 "Subject Alternative Name"
  ```

### Nginx sirve un certificado viejo o autofirmado

**Causas posibles:**

**A) Docker montó un volumen con certificados viejos:**
```bash
docker compose down
# Verificar que nginx/certs/ tiene los PEM correctos
ls -la nginx/certs/
docker compose up -d
```

**B) La imagen se construyó con COPY y no se reconstruyó:**
```bash
docker compose down -v
docker compose build --no-cache nginx
docker compose up -d
```

### HSTS cacheado en Chromium/Chrome

Chromium cachea agresivamente las políticas HSTS. Si antes visitaste
el dominio con un certificado malo, puede seguir bloqueándolo.

Limpiar:
1. Abrir `chrome://net-internals/#hsts`
2. En **Delete domain security policies**, escribir `economy.local.app`
3. Click en **Delete**

### Surfshark rompe certificados locales

Surfshark (especialmente la versión Flatpak) interfiere con:
- La base de datos NSS
- El trust store del sistema
- La resolución DNS local
- Los certificados locales

Cuando falle algo relacionado con SSL, probar:
```bash
flatpak kill com.surfshark.Surfshark
```
Luego reiniciar el navegador.

### Certificado autofirmado (Issuer NO es mkcert)

Si al verificar el certificado aparece `Issuer: CN=economy.local.app` en
lugar de `Issuer: O=mkcert development CA`, significa que se generó con
`openssl` en vez de `mkcert`.

**Solución:** volver al paso 5 y regenerar con mkcert.

**NUNCA uses:**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 ...
```
Esto siempre genera certificados autofirmados que los navegadores rechazan.

---

## Archivos del proyecto

| Archivo | Propósito |
|---------|-----------|
| `nginx/nginx.conf` | Configuración de Nginx (SSL, proxy, upstreams) |
| `nginx/certs/economy.local.app.pem` | Certificado SSL |
| `nginx/certs/economy.local.app-key.pem` | Clave privada SSL |
| `docker-compose.yml` | Volúmenes de nginx montan `nginx/` y `nginx/certs/` |

## Comandos rápidos de diagnóstico

```bash
# ¿Qué certificado sirve nginx?
openssl s_client -connect economy.local.app:443 -servername economy.local.app 2>/dev/null | openssl x509 -noout -issuer -subject

# ¿Qué cubre el certificado?
openssl x509 -in nginx/certs/economy.local.app.pem -text -noout | grep -A1 "Subject Alternative Name"

# ¿Está la CA instalada?
certutil -L -d sql:$HOME/.pki/nssdb

# ¿Resuelve el dominio?
ping -c 1 economy.local.app

# ¿Nginx funciona?
docker exec -it economy_nginx nginx -t
```
