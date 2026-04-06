# Build context: ./clients (monorepo root)
# docker build -f apps/web/Dockerfile .

FROM node:24-alpine AS base
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

ARG NEXT_PUBLIC_API_URL="https://dev-api.solei.to"
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ARG NEXT_PUBLIC_FRONTEND_BASE_URL="http://dev.solei.to"
ENV NEXT_PUBLIC_FRONTEND_BASE_URL=${NEXT_PUBLIC_FRONTEND_BASE_URL}
ARG NEXT_PUBLIC_BACKOFFICE_URL="http://dev-api.solei.to/backoffice"
ENV NEXT_PUBLIC_BACKOFFICE_URL=${NEXT_PUBLIC_BACKOFFICE_URL}
ARG NEXT_PUBLIC_STRIPE_KEY="__UNSET__"
ENV NEXT_PUBLIC_STRIPE_KEY=${NEXT_PUBLIC_STRIPE_KEY}
ARG NEXT_PUBLIC_GITHUB_APP_NAMESPACE="__UNSET__"
ENV NEXT_PUBLIC_GITHUB_APP_NAMESPACE=${NEXT_PUBLIC_GITHUB_APP_NAMESPACE}
ARG NEXT_PUBLIC_APPLE_DOMAIN_ASSOCIATION="__UNSET__"
ENV NEXT_PUBLIC_APPLE_DOMAIN_ASSOCIATION=${NEXT_PUBLIC_APPLE_DOMAIN_ASSOCIATION}

# SENTRY_AUTH_TOKEN is passed as a build secret so it never lands in a layer.
# If not provided (e.g. fork PRs), the var is left unset and Sentry skips upload.
RUN --mount=type=secret,id=SENTRY_AUTH_TOKEN \
    if [ -f /run/secrets/SENTRY_AUTH_TOKEN ]; then \
      export SENTRY_AUTH_TOKEN="$(cat /run/secrets/SENTRY_AUTH_TOKEN)"; \
    fi; \
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

ENV S3_PUBLIC_IMAGES_BUCKET_PROTOCOL="http"
ENV S3_PUBLIC_IMAGES_BUCKET_HOSTNAME="127.0.0.1"
ENV S3_PUBLIC_IMAGES_BUCKET_PORT="9000"
ENV S3_PUBLIC_IMAGES_BUCKET_PATHNAME="**"
ENV S3_UPLOAD_ORIGINS="http://127.0.0.1:9000"

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "apps/web/server.js"]
