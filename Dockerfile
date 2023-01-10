# select you base image to start with
FROM node:lts-alpine

ENV NODE_ENV=production

# create app dependencies
# location inside the container
WORKDIR /usr/src/app

# install app dependencies
# 
COPY ["package.json", "package-lock.json*", "npm-shrinkwrap.json*", "./"]
RUN npm install --production --silent && mv node_modules ../
COPY . .
EXPOSE 3000
RUN chown -R node /usr/src/app
USER node
CMD ["node", "index.js"]
