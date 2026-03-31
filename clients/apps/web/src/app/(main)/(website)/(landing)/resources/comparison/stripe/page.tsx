import { PolarVsStripePage } from '@/components/Landing/comparison/PolarStripePage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Solei vs Stripe',
  description:
    'Compare Solei with Stripe for Africa-first billing and payment integrations.',
  keywords:
    'solei vs stripe, africa payments, african payment systems, billing infrastructure, merchant of record, fintech for africa, payment integrations',
  openGraph: {
    siteName: 'Solei',
    type: 'website',
    title: 'Solei vs Stripe',
    description:
      'Solei is built for Africa and integrates with African payment systems.',
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
    title: 'Solei vs Stripe',
    description:
      'Solei is built for Africa and integrates with African payment systems.',
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
  return <PolarVsStripePage />
}
