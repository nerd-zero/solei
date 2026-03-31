import type { Metadata } from 'next'

const BLOG_SLUG = 'launching-solei-billing-layer-for-africa' as const
const BLOG_COVER = '/assets/landing/blog/solei-launch-cover.svg' as const

export const dynamic = 'force-static'
export const dynamicParams = false

export async function generateStaticParams() {
  return [{ slug: BLOG_SLUG }]
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params

  if (slug !== BLOG_SLUG) {
    return {}
  }

  return {
    title: 'Launching Solei: the billing layer for Africa',
    description:
      'One of the many tools built by Nerd Zero, a small team of developers daring to build fintech tools for Africa.',
    openGraph: {
      title: 'Launching Solei: the billing layer for Africa',
      description:
        'One of the many tools built by Nerd Zero, a small team of developers daring to build fintech tools for Africa.',
      images: [BLOG_COVER],
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Launching Solei: the billing layer for Africa',
      description:
        'One of the many tools built by Nerd Zero, a small team of developers daring to build fintech tools for Africa.',
      images: [BLOG_COVER],
    },
  }
}

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params

  if (slug !== BLOG_SLUG) {
    throw new Error('Not found')
  }

  const { default: Post } = await import(
    '../_posts/launching-solei-billing-layer-for-africa/page.mdx'
  )

  return <Post />
}
