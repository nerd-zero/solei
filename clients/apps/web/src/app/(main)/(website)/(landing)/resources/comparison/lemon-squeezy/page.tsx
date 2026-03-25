import { PolarVsLemonSqueezyPage } from '@/components/Landing/comparison/PolarLemonSqueezyPage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Solei vs Lemon Squeezy',
  description: 'Comparing Solei and Lemon Squeezy',
  keywords:
    'polar vs lemon squeezy, lemon squeezy, polar, comparison, pricing, pricing for polar, pricing for polar, pricing for polar',
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
  return <PolarVsLemonSqueezyPage />
}
