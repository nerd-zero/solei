import { investors } from './investors'

// ── Page ──────────────────────────────────────────────────────────────────────

export default function CompanyPage() {
  return (
    <div className="dark:bg-polar-950 min-h-screen bg-white text-gray-900 dark:text-white">
      {/* Hero */}
      <section className="flex flex-col items-center gap-8 px-4 pt-12 pb-24 text-center">
        <h1 className="font-display leading-tighter max-w-2xl text-5xl font-medium text-balance md:text-7xl">
          We&apos;re building the billing layer for Africa. Are you in?
        </h1>
        <p className="max-w-xl text-lg text-balance">
          Forget legacy systems. We&apos;re using modern software to help
          businesses charge, collect, and reconcile payments across borders
          without the headache.
        </p>
      </section>

      {/* About */}
      <section className="mx-auto flex w-full max-w-xl flex-col gap-8 py-24 md:px-6">
        <h2 className="font-display text-2xl font-medium md:text-4xl">
          The Mission
        </h2>
        <div className="flex flex-col gap-4 text-lg leading-relaxed">
          <p>Big ambitions for the next generation of African enterprise.</p>
          <p>The Team: Small, fast-moving, and highly autonomous.</p>
          <p>The Tech: Open-source, transparent, and built for reliability.</p>
        </div>
      </section>

      {/* Advisors */}
      <section>
        <div className="mx-auto max-w-xl py-16 md:px-6">
          <div className="mb-12 flex flex-col gap-3">
            <h2 className="font-display text-3xl font-medium">
              Angels, Advisors & Supporters
            </h2>
            <p className="text-lg">
              We&apos;re actively looking for angels and advisors who believe in
              the future of African infrastructure. If you&apos;ve built,
              backed, or scaled great companies, we&apos;d love to hear from
              you.
            </p>
            <div>
              <a
                href="mailto:hello@solei.to"
                className="mt-2 inline-flex items-center rounded-full bg-gray-900 px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-80 dark:bg-white dark:text-gray-900"
              >
                Become an Angel or Advisor
              </a>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-6">
            {investors.map((investor) => (
              <div key={investor.name} className="flex flex-col gap-0.5">
                <span className="font-medium">{investor.name}</span>
                <span className="dark:text-polar-500 text-gray-500">
                  {investor.company}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Join */}
      <section className="dark:border-polar-800 border-t border-gray-100">
        <div className="mx-auto flex max-w-xl flex-col gap-6 py-16 md:px-6">
          <h2 className="font-display text-3xl font-medium">
            Want to help shape the future?
          </h2>
          <p className="text-lg leading-relaxed">
            We&apos;re building the systems that power modern billing across the
            continent. If that resonates, let&apos;s talk.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <a
              href="mailto:hello@solei.to"
              className="inline-flex items-center justify-center rounded-full bg-gray-900 px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-80 dark:bg-white dark:text-gray-900"
            >
              Contact Us
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
