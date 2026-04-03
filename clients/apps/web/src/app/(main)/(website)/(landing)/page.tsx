import { Metadata } from 'next'
import LandingPage from '../../../../components/Landing/LandingPage'
export const metadata: Metadata = {
  title: 'Solei — Monetize your software with ease',
  description: 'A billing layer for Africa',
  keywords:
    'monetization, billing, payments, africa, saas, digital products, platform, developer, open source, economy',
  openGraph: {
    siteName: 'Solei',
    type: 'website',
    images: [
      {
        url: 'https://solei.to/assets/brand/solei_og.jpg',
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    images: [
      {
        url: 'https://solei.to/assets/brand/solei_og.jpg',
        width: 1200,
        height: 630,
        alt: 'Solei',
      },
    ],
  },
}

export default function Page() {
  return <LandingPage />
}
