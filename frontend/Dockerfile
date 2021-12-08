# build env
FROM node:14-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
CMD cp -r build result_build


# node:13.12.0-alpine более не существует