# Solei

**Open-source payments infrastructure built for the African digital economy.**

[Website](https://solei.to) • [Docs](https://docs.solei.to) • [API Reference](https://docs.solei.to/api-reference)

---

## Empowering African Developers & Creators

Focus on what you build—**Solei** handles the infrastructure that gets you paid across the continent.

- **Launch SaaS & digital products** in minutes with global + local checkout.
- **Localized payments** with African gateways & mobile money _(coming soon)_.
- **Unified monetization** for indie hackers, dev shops, and communities.
- **Digital storefronts** for GitHub repos, Discord channels, file downloads, and license keys.
- **Operational essentials** handled for you: billing, receipts, taxes, and customer accounts.

## Pricing (Solei Africa)

- **Competitive local rates** optimized for regional growth.
- **Zero fixed monthly fees**—scale at your pace.
- **Transparent transaction fees** published on our website.

---

## Acknowledgments & Lineage

**Solei** began as a fork of the excellent [Polar](https://polar.sh) platform. We are deeply grateful to the **Polar Software Inc.** team and contributors for building such a powerful open-source foundation.

Today, Solei is maintained independently by **Nerd Zero**, laser-focused on the African market while honoring the groundwork laid by the Polar community.

## Monorepo Structure

- **[server](./server/README.md)** – Python · FastAPI · Dramatiq · SQLAlchemy (Postgres) · Redis
- **[clients](./clients/README.md)** – Turborepo
    - [web](./clients/apps/web) (Solei Dashboard) – Next.js (TypeScript)
    - [ui](./clients/packages/ui) – Shared React components

## License & Legal

Licensed under the **Apache License, Version 2.0**.

Original code Copyright © 2023 Polar Software Inc.
Modifications & new features Copyright © 2026 **Nerd Zero**.
