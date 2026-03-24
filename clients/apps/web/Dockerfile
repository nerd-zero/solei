# Build context: ./clients (monorepo root)
# docker build -f apps/web/Dockerfile .

FROM node:22-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# ---- Builder ----
FROM base AS builder
WORKDIR /app

COPY . .
RUN pnpm install --frozen-lockfile

ARG RELEASE_VERSION
ENV NEXT_PUBLIC_RELEASE_VERSION=${RELEASE_VERSION}

# SENTRY_AUTH_TOKEN is passed as a build secret so it never lands in a layer.
# If not provided (e.g. fork PRs), source map upload is silently skipped.
RUN --mount=type=secret,id=SENTRY_AUTH_TOKEN \
    SENTRY_AUTH_TOKEN=$(cat /run/secrets/SENTRY_AUTH_TOKEN 2>/dev/null || true) \
    pnpm --filter "web..." build

# ---- Runner ----
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# next.config.mjs output: standalone copies only what's needed to run the server
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "apps/web/server.js"]
