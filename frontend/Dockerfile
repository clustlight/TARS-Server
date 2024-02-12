FROM node:18-slim AS builder

ENV NEXT_TELEMETRY_DISABLED 1
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production=false
COPY ../../TARS-UI .
RUN yarn build

FROM gcr.io/distroless/nodejs:18 AS runner
ENV NODE_ENV=production

WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/.next/static ./.next/static

COPY --from=builder /app/.next/standalone ./
CMD ["server.js"]