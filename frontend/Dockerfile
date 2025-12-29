# ---------- Build stage ----------
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# ---------- Runtime stage ----------
FROM node:18-alpine
WORKDIR /app

COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["node", "-e", "\
const http=require('http');\
const fs=require('fs');\
const path=require('path');\
const base=path.join(process.cwd(),'build');\
http.createServer((req,res)=>{\
  const p=req.url==='/'?'index.html':req.url;\
  const f=path.join(base,p);\
  fs.readFile(f,(e,d)=>{\
    if(e){res.writeHead(404);res.end('Not Found');return;}\
    res.end(d);\
  });\
}).listen(3000);\
"]

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