import { PolarVsStripePage } from '@/components/Landing/comparison/PolarStripePage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Solei vs Stripe',
  description: 'Comparing Solei and Stripe',
  keywords:
    'polar vs stripe, stripe, polar, comparison, pricing, pricing for polar, pricing for polar, pricing for polar',
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
  return <PolarVsStripePage />
}
