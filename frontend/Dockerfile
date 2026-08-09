# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve static files using Nginx
FROM nginx:alpine

# Copy the build output to Nginx HTML directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration if needed for SPA routing, or use standard configuration
# Expose port 80 for traffic
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
