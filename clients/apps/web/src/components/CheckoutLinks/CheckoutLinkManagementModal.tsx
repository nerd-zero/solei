import { schemas } from '@polar-sh/client'
import Link from 'next/link'
import { CheckoutLinkForm } from './CheckoutLinkForm'

interface CheckoutLinkManagementModalProps {
  organization: schemas['Organization']
  onClose: (checkoutLink: schemas['CheckoutLink']) => void
  productIds: string[]
}

export const CheckoutLinkManagementModal = ({
  organization,
  onClose,
  productIds,
}: CheckoutLinkManagementModalProps) => {
  if (!organization.country) {
    return (
      <div className="flex h-full flex-col gap-8 overflow-y-auto px-8 py-12">
        <div className="flex flex-row items-center justify-between">
          <h1 className="text-xl">Create Checkout Link</h1>
        </div>
        <div className="dark:bg-polar-800 rounded-xl border border-amber-200 bg-amber-50 p-6 dark:border-amber-700/50">
          <p className="font-medium text-amber-900 dark:text-amber-400">
            Country required
          </p>
          <p className="mt-1 text-sm text-amber-800/70 dark:text-amber-300/70">
            Your organization must have a country set before you can create
            checkout links. Go to{' '}
            <Link
              href={`/dashboard/${organization.slug}/settings`}
              className="underline"
            >
              organization settings
            </Link>{' '}
            to add your country.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col gap-8 overflow-y-auto px-8 py-12">
      <div className="flex flex-row items-center justify-between">
        <h1 className="text-xl">Create Checkout Link</h1>
      </div>
      <CheckoutLinkForm
        organization={organization}
        onClose={onClose}
        productIds={productIds}
      />
    </div>
  )
}
