# Stage 1: Build the Nuxt application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json only to avoid lockfile conflicts across platforms
COPY package.json ./

# Install build tools for native dependencies (if any)
RUN apk add --no-cache python3 make g++

# Install dependencies (generating a new package-lock.json)
RUN npm install --legacy-peer-deps

# Copy the rest of the application source code
COPY . .

# Build the application for production
# This will create the .output directory
RUN npm run build

# Stage 2: Create the final production image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy the built application from the builder stage
# This includes the server, public assets, etc.
COPY --from=builder /app/.output .

# Expose the port the app runs on (default for Nuxt is 3000)
EXPOSE 3000

# The command to start the Nuxt production server
# The entrypoint is located at .output/server/index.mjs
CMD ["node", "server/index.mjs"]
