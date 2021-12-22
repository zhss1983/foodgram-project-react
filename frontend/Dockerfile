# build env
FROM node:14-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm cache clean -f
RUN npm install
COPY . ./
RUN npm run build
CMD cp -r build result_build
