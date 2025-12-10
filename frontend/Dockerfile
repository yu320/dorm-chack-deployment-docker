# Stage 1: Build the Nuxt application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install build tools
RUN apk add --no-cache python3 make g++

# Copy all source code first to ensure nuxt prepare has context
COPY . .

# Force clean install: Remove host lockfile to avoid Windows/Linux conflicts
# We also clean node_modules just in case, though .dockerignore should exclude it
RUN rm -rf package-lock.json node_modules

# Install dependencies ignoring scripts first
RUN npm install --legacy-peer-deps --ignore-scripts

# Explicitly install the missing binding for Alpine (musl)
RUN npm install --cpu=x64 --os=linux --libc=musl -D @oxc-parser/binding-linux-x64-musl

# Rebuild and run postinstall (nuxt prepare)
RUN npm rebuild && npm run postinstall

# Build the application for production
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
