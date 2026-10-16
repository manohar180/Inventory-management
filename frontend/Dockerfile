FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
 
RUN npm ci

COPY . .

RUN npm run build

# ----------------- Stage 2: Runtime -----------------
FROM nginxinc/nginx-unprivileged:alpine-slim

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

USER 101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
