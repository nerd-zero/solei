import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Company',
  description: 'We are building the billing layer for Africa.',
  openGraph: {
    title: 'Company',
    description: 'We are building the billing layer for Africa.',
  },
  twitter: {
    card: 'summary',
    title: 'Company',
    description: 'We are building the billing layer for Africa.',
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
