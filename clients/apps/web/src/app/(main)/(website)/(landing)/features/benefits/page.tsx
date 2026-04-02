import { BenefitsPage } from '@/components/Landing/features/BenefitsPage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Product benefits & fulfillment — Solei',
  description:
    'Automate product benefits with license keys, file downloads, GitHub access, Discord roles, and custom integrations.',
  keywords:
    'product benefits, license keys, digital downloads, github access, discord integration, benefit fulfillment',
  openGraph: {
    siteName: 'solei.to',
    type: 'website',
    images: [
      {
        url: 'https://solei.to/company',
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    images: [
      {
        url: 'https://solei.to/company',
        width: 1200,
        height: 630,
        alt: 'solei.to',
      },
    ],
  },
}

export default function Page() {
  //test build
  return <BenefitsPage />
}
