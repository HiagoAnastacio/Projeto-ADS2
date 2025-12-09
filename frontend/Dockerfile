# ---- Stage 1: Build (Node.js) ----
FROM node:18-alpine as build

WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o código fonte
COPY . .

# Build da aplicação (Vite)
# Isso vai gerar a pasta 'dist' com os estáticos otimizados
RUN npm run build

# ---- Stage 2: Serve (Nginx) ----
FROM nginx:alpine

# Copia o build gerado no Stage 1 para a pasta do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copia nossa configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# O Nginx expõe a porta 80 por padrão
EXPOSE 80

# Inicia o Nginx (comando padrão da imagem)
CMD ["nginx", "-g", "daemon off;"]
