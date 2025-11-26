# Stage 1: Build the Nuxt application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install compatibility libraries and build tools for Alpine
# python3, make, g++ are often needed for compiling native modules (like node-sass or sharp)
RUN apk add --no-cache libc6-compat python3 make g++

# Copy package.json (we ignore package-lock.json to avoid platform conflicts)
COPY package.json ./

# Install dependencies
# We deliberately do NOT use 'npm ci' because the package-lock.json might be generated on Windows
# and cause issues on Linux/Alpine. A fresh 'npm install' ensures Linux-compatible dependencies.
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the application for production
RUN npm run build

# Stage 2: Create the final production image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy the built application from the builder stage
COPY --from=builder /app/.output .

# Expose the port
EXPOSE 3000

# The command to start the Nuxt production server
CMD ["node", "server/index.mjs"]
