import type { Metadata } from 'next'

const BLOG_SLUG = 'launching-solei-billing-layer-for-africa' as const
const BLOG_COVER = '/assets/landing/blog/solei-launch-cover.svg' as const
const BLOG_TITLE = 'Launching Solei, the billing layer for Africa' as const
const BLOG_DESCRIPTION =
  'One of the many tools built by Nerd Zero, a small team of developers daring to build fintech tools for Africa.' as const

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
    title: BLOG_TITLE,
    description: BLOG_DESCRIPTION,
    openGraph: {
      title: BLOG_TITLE,
      description: BLOG_DESCRIPTION,
      images: [BLOG_COVER],
    },
    twitter: {
      card: 'summary_large_image',
      title: BLOG_TITLE,
      description: BLOG_DESCRIPTION,
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
