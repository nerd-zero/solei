import { AnalyticsPage } from '@/components/Landing/features/AnalyticsPage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Analytics and Insights — Solei',
  description:
    'Comprehensive analytics dashboard with revenue metrics, customer insights, and growth tracking for your SaaS business.',
  keywords:
    'saas analytics, revenue metrics, customer insights, mrr tracking, saas dashboard, business analytics',
  openGraph: {
    siteName: 'Solei',
    type: 'website',
    images: [
      {
        url: 'https://solei.to/assets/brand/polar_og.jpg',
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    images: [
      {
        url: 'https://solei.to/assets/brand/polar_og.jpg',
        width: 1200,
        height: 630,
        alt: 'Solei',
      },
    ],
  },
}

export default function Page() {
  return <AnalyticsPage />
}
