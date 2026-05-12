import ManualPayout from '@/components/Icons/ManualPayout'
import Paystack from '@/components/Icons/Paystack'
import Stripe from '@/components/Icons/Stripe'
import { schemas } from '@polar-sh/client'

export const ACCOUNT_TYPE_DISPLAY_NAMES: Record<
  schemas['AccountType'],
  string
> = {
  stripe: 'Stripe',
  manual: 'Manual',
  paystack: 'Paystack',
}
export const ACCOUNT_TYPE_ICON: Record<schemas['AccountType'], React.FC> = {
  stripe: Stripe,
  manual: ManualPayout,
  paystack: Paystack,
}
