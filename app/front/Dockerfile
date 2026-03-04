FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .

RUN npm run build

# Serve with Nginx
FROM nginx:alpine
# Copy Angular 17+ /browser output into the path nginx.conf expects
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html/browser
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]