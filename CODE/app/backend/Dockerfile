FROM node:10-alpine

ENV APP_HOST=0.0.0.0
ENV APP_PORT=3000
ENV ROOT_DIR=/app

WORKDIR /app

COPY . /app

RUN chmod 777 wait-for-it.sh

RUN npm i

EXPOSE 3000 

CMD [ "npm", "start" ]