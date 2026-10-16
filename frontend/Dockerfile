# ==============================================================================
# StockPilot Frontend Dockerfile
# Stage 1: Build static assets using Node
# Stage 2: Serve static bundle via unprivileged non-root Nginx
# ==============================================================================

# ----------------- Stage 1: Build -----------------
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./

# Install dependencies deterministically
RUN npm ci

# Copy application source code
COPY . .

# Compile production bundle to /app/dist
RUN npm run build

# ----------------- Stage 2: Runtime -----------------
FROM nginxinc/nginx-unprivileged:alpine-slim

# Copy compiled SPA static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy unprivileged Nginx server configuration (listens on 8080)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Unprivileged Nginx automatically runs as user 'nginx' (UID 101)
USER 101

# Expose unprivileged HTTP port
EXPOSE 8080

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
