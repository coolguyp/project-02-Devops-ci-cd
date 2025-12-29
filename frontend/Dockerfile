# ---------- Build ----------
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# ---------- Runtime ----------
FROM node:18-alpine
WORKDIR /app

# Install only what is needed to serve static files
RUN npm install -g serve \
 && rm -rf /root/.npm /tmp/*

COPY --from=builder /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]

## -------- Build stage --------
#FROM public.ecr.aws/docker/library/node:18-alpine AS builder
#
#WORKDIR /app
#
#RUN apk update && apk upgrade openssl
#
#COPY package.json package-lock.json* ./
#RUN npm install
#
#COPY . .
#RUN npm run build
#
## -------- Runtime stage --------
#FROM public.ecr.aws/docker/library/node:18-alpine
#
#WORKDIR /app
#
#RUN apk update && apk upgrade openssl \
# && npm install -g serve \
# && rm -rf /var/cache/apk/*
#
#COPY --from=builder /app/build ./build
#
#EXPOSE 3000
#CMD ["serve", "-s", "build", "-l", "3000"]
#