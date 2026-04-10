FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src

# Build application
RUN npm run build

# Install a simple server
RUN npm install -g serve

# Expose port
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1

# Start application
CMD ["serve", "-s", "dist", "-l", "8080"]
