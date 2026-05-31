FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

ARG VITE_DEBOUNCE_MS
ARG VITE_MIN_QUERY_LENGTH
ENV VITE_DEBOUNCE_MS=$VITE_DEBOUNCE_MS
ENV VITE_MIN_QUERY_LENGTH=$VITE_MIN_QUERY_LENGTH

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
