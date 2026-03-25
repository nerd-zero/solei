import { MORPage } from '@/components/Landing/resources/MORPage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Merchant of Record',
  description: 'A deep dive into Merchant of Records & what they mean for you',
  keywords:
    'mor, merchant of record, lemon squeezy, paddle, taxes, compliance, monetization',
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
  return <MORPage />
}
