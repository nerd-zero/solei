# Rebrand TODO — Polar → Solei

Items intentionally left behind during the initial automated rebrand, with exact locations.
Check each off as you complete it.

---

## 1. npm Scope: `@polar-sh` → `@solei-sh` (or `@nerd-zero`)

All workspace packages still use the `@polar-sh` scope. These were kept as-is to avoid
breaking internal workspace references prematurely. Rename all at once when ready to
publish to npm.

**Packages to rename:**
- `clients/packages/checkout/package.json` — `@polar-sh/checkout`
- `clients/packages/client/package.json` — `@polar-sh/client`
- `clients/packages/currency/package.json` — `@polar-sh/currency`
- `clients/packages/eslint-config/package.json` — `@polar-sh/eslint-config`
- `clients/packages/i18n/package.json` — `@polar-sh/i18n`
- `clients/packages/mdx/package.json` — `@polar-sh/mdx`
- `clients/packages/orbit/package.json` — `@polar-sh/orbit`
- `clients/packages/typescript-config/package.json` — `@polar-sh/typescript-config`
- `clients/packages/ui/package.json` — `@polar-sh/ui`
- `clients/apps/app/package.json` — `@polar-sh/app`
- `clients/apps/web/package.json` — `@polar-sh/web`
- `clients/examples/checkout-embed/package.json` — `@polar-sh/checkout-embed`

**Also update all internal cross-references** (imports like `@polar-sh/ui`, `@polar-sh/client`, etc.)
across `clients/apps/web/`, `clients/apps/app/`, and other packages.

---

## 2. Tailwind CSS Color Classes: `polar-*` → `solei-*`

The design system uses custom color names `polar-700`, `polar-800`, etc. These appear
in **323 files** under `clients/`. They map to Tailwind config in:

- `clients/packages/ui/tailwind.config.ts` — defines the `polar` color palette key

**Steps:**
1. Rename the color key in `tailwind.config.ts` from `polar` to `solei`
2. Do a global find-and-replace across `clients/` from `polar-50` through `polar-950`
   (and `polar/` opacity variants like `polar-700/10`) to `solei-50` … `solei-950`

---

## 3. React Provider Component Names

Internal component names still reference `Polar`:

| File | Component |
|------|-----------|
| `clients/apps/web/src/app/providers.tsx` | `PolarPostHogProvider`, `PolarQueryClientProvider`, `PolarNuqsProvider` |
| `clients/apps/web/src/app/layout.tsx` | Imports/uses above providers |
| `clients/apps/app/providers/PolarQueryClientProvider.tsx` | File name + export |
| `clients/apps/app/app/(authenticated)/_layout.tsx` | Imports `PolarQueryClientProvider` |

Rename to `SoleiPostHogProvider`, `SoleiQueryClientProvider`, `SoleiNuqsProvider` and
rename the file `PolarQueryClientProvider.tsx` → `SoleiQueryClientProvider.tsx`.

---

## 4. External SDK: `@polar-sh/sdk` (npm) → Fork or Replace

`clients/apps/web/package.json` depends on the *published* npm package (not the workspace copy):

```
"@polar-sh/sdk": "^0.46.1"
```

This pulls Polar's client SDK from npm. Options:
- **Replace with workspace `@polar-sh/client`** if feature-equivalent
- **Fork** `@polar-sh/sdk` into this repo, rebrand, and publish as `@solei-sh/sdk`

Until resolved, any API shape changes to the upstream SDK will not be reflected automatically.

---

## 5. External Python SDK: `polar-sdk` (PyPI) → Fork or Replace

`server/pyproject.toml` line 86:

```
"polar-sdk==0.27.3",
```

This is the upstream Polar Python SDK from PyPI. Options:
- **Replace with internal API calls** directly
- **Fork** into `server/` as a local package, rebrand as `solei-sdk`, and publish to PyPI

---

## 6. S3 Image Assets: `polar-public-assets.s3.amazonaws.com` → Solei Bucket

Email header and icon components still reference Polar's S3 bucket because Solei's
replacement assets don't exist yet:

| File | Line(s) |
|------|---------|
| `server/emails/src/components/SoleiHeader.tsx` | Logo image URL |
| `server/emails/src/components/Icons.tsx` | Icon image URLs |

**Blocked on:** Creating a `solei-public-assets` S3 bucket (or equivalent CDN) and
uploading rebranded logo/icon assets. Once done, update the `src` URLs in both files.

---

## 7. Static OG Image: `polar_og.jpg` → `solei_og.jpg`

17 landing pages reference a non-existent asset path:

```
https://solei.to/assets/brand/polar_og.jpg
```

Files affected — all under `clients/apps/web/src/app/(main)/(website)/(landing)/`:
- `page.tsx`, `features/finance/page.tsx`, `features/products/page.tsx`,
  `features/usage-billing/page.tsx`, `resources/page.tsx`, `resources/why/page.tsx`,
  `resources/comparison/lemon-squeezy/page.tsx`, `resources/comparison/paddle/page.tsx`,
  `resources/comparison/stripe/page.tsx`, `customers/page.tsx`, `downloads/page.tsx`,
  `features/analytics/page.tsx`, `features/benefits/page.tsx`, `features/customers/page.tsx`,
  `resources/merchant-of-record/page.tsx`, `resources/pricing/page.tsx`
- `clients/apps/web/src/app/layout.tsx`

**Steps:**
1. Create a `solei_og.jpg` brand asset (1200×630 recommended)
2. Place at `clients/apps/web/public/assets/brand/solei_og.jpg`
3. Find-and-replace `polar_og.jpg` → `solei_og.jpg` across the 17 files above

---

## 8. Logfire Telemetry: `polarsource/polar` repo reference

`server/solei/logfire.py` line 164:

```python
repository="https://github.com/polarsource/polar",
```

This is the repository URL sent with error telemetry. Update to:

```python
repository="https://github.com/nerd-zero/solei",
```

(or wherever the Solei repo is hosted)

---

## 9. Config: Favicon & Thumbnail URLs pointing to `polarsource/polar` on GitHub

`server/solei/config.py` lines 250–251:

```python
FAVICON_URL: str = "https://raw.githubusercontent.com/polarsource/polar/..."
THUMBNAIL_URL: str = "https://raw.githubusercontent.com/polarsource/polar/..."
```

These are fallback URLs used for checkout pages. Replace with Solei-hosted equivalents
once brand assets are available (see item 7 above).

---

## 10. `polarsource` GitHub Org References (Attribution vs. Brand)

Some references to `polarsource` and `polarsource/polar` are *attribution* (fine to keep
under Apache 2.0) vs. *brand* (should be updated). Review each:

| File | Context | Action |
|------|---------|--------|
| `server/solei/logfire.py:164` | Repo URL in telemetry | Update (see item 8) |
| `server/solei/config.py:250-251` | Asset URLs | Update (see item 9) |
| `server/solei/benefit/strategies/github_repository/schemas.py` | Possibly example org name | Review |
| `server/solei/metrics/queries.py` | Check context | Review |
| `clients/packages/client/src/v1.ts` | Check context | Review |
| `DEVELOPMENT.md` | Setup / attribution docs | Review, update brand sections |
| `SECURITY.md` | Security contact or attribution | Review |
| `clients/apps/web/src/app/humans.txt/route.tsx` | Credit / attribution | Review |
| `clients/apps/web/src/components/Landing/resources/WhyPolarPage.tsx` | Landing copy | Update or remove |
| `clients/apps/web/src/components/Organization/Footer.tsx` | Footer links | Review |
| `clients/apps/web/src/components/Landing/LandingLayout.tsx` | Meta/links | Review |
| `clients/apps/web/src/components/Meter/MeterPage.tsx` | Docs link? | Review |
| Server test fixtures and testdata HTML files | Test data only | Low priority |

---

## 11. Comparison Landing Pages (Polar branding in filenames & copy)

These pages compare Solei against competitors using filenames that still say `Polar`:

- `clients/apps/web/src/components/Landing/comparison/PolarLemonSqueezyPage.tsx`
- `clients/apps/web/src/components/Landing/comparison/PolarPaddlePage.tsx`
- `clients/apps/web/src/components/Landing/comparison/PolarStripePage.tsx`

Rename files and update copy: `Polar vs. X` → `Solei vs. X`.

---

## Priority Order

| Priority | Item | Blocker |
|----------|------|---------|
| High | Item 6 — S3 assets | Need new S3 bucket + assets |
| High | Item 7 — OG image | Need brand asset |
| High | Item 8 — Logfire repo URL | None |
| High | Item 9 — Config asset URLs | Need brand assets |
| Medium | Item 3 — React provider names | None |
| Medium | Item 11 — Comparison page names | None |
| Medium | Item 10 — polarsource review pass | None |
| Low | Item 2 — Tailwind color classes | None (cosmetic) |
| Low | Item 4 — External JS SDK | Architecture decision |
| Low | Item 5 — External Python SDK | Architecture decision |
| Defer | Item 1 — npm scope | Pre-publish task |
