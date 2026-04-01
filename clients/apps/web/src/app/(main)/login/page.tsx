import Login from '@/components/Auth/Login'
import { PolarLogotype } from '@/components/Layout/Public/PolarLogotype'
import { CONFIG } from '@/utils/config'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Log in to Solei',
}

export default async function Page(props: {
  searchParams: Promise<{
    return_to?: string
    from?: string
  }>
}) {
  const searchParams = await props.searchParams

  const { return_to, ...rest } = searchParams

  return (
    <div className="flex h-screen w-full grow items-center justify-center">
      <div className="dark:bg-polar-900 flex w-full max-w-md flex-col justify-between gap-8 rounded-3xl bg-gray-50 p-12">
        <div className="flex flex-col gap-y-4">
          <PolarLogotype className="h-[60px] w-[60px]" />
          <div className="flex flex-col gap-4">
            <h2 className="text-2xl text-black dark:text-white">
              {CONFIG.IS_SANDBOX
                ? 'Welcome to the Solei Sandbox'
                : 'Welcome to Solei'}
            </h2>
            <span className="dark:text-polar-400 text-lg text-balance text-gray-500">
              {CONFIG.IS_SANDBOX ? (
                <>
                  This is a testing environment. Changes here won&rsquo;t affect
                  your live account and payments are not processed.
                </>
              ) : (
                'Monetize your software'
              )}
            </span>
          </div>
        </div>
        <Login returnTo={return_to} returnParams={rest} />
      </div>
    </div>
  )
}
