FROM node:18.16-alpine

EXPOSE 3000
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

COPY ./frontend /home/frontend
WORKDIR /home/frontend

RUN apk update && apk upgrade && \
    apk add git

RUN npm install && \
    npm run build
CMD [ "npm", "start" ]