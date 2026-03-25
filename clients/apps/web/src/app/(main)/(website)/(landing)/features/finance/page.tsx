import { FinancePage } from '@/components/Landing/features/FinancePage'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Finance & Payouts — Solei',
  description:
    'Transparent financial reporting with automatic tax handling, global payouts, and detailed revenue tracking.',
  keywords:
    'finance, payouts, invoicing, tax compliance, revenue tracking, payment reporting',
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
  return <FinancePage />
}
