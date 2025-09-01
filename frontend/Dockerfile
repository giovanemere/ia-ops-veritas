FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/

RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactjs -u 1001

RUN chown -R reactjs:nodejs /app
USER reactjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["npm", "start"]
