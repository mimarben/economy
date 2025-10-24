# Client Dockerfile
# last LTS at October 2025
FROM node:22.21.0

# Directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json primero
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar todo el código
COPY . .

# Construir la app para producción
RUN npm run build

# Servir con un servidor estático, por ejemplo serve
RUN npm install -g serve

# Exponer puerto
EXPOSE 3000

# Comando por defecto
#CMD ["serve", "-s", "build", "-l", "4200"]

# Comando por defecto: modo desarrollo
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
