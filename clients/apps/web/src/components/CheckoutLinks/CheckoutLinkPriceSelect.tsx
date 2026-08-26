import { isStaticPrice } from '@/utils/product'
import { schemas } from '@polar-sh/client'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@polar-sh/ui/components/atoms/Select'
import { formatCurrency } from '@polar-sh/currency'
import React, { useMemo } from 'react'

const AUTOMATIC_VALUE = 'automatic'

const getPriceLabel = (
  price: schemas['ProductPrice'],
  product: schemas['Product'],
): string => {
  const currency = price.price_currency.toUpperCase()
  const interval = product.recurring_interval
    ? ` / ${product.recurring_interval}`
    : ''

  switch (price.amount_type) {
    case 'fixed':
      return `${formatCurrency('standard')(price.price_amount, price.price_currency)} ${currency}${interval}`
    case 'free':
      return `Free (${currency})`
    case 'custom':
      return `Pay what you want (${currency})`
    case 'seat_based': {
      const [firstTier] = price.seat_tiers.tiers
      if (!firstTier) {
        return `Seat-based (${currency})`
      }
      return `From ${formatCurrency('standard')(firstTier.price_per_seat, price.price_currency)} ${currency} / seat${interval}`
    }
    default:
      return currency
  }
}

interface CheckoutLinkPriceSelectProps {
  product: schemas['Product'] | undefined
  value: string | null
  onChange: (value: string | null) => void
}

const CheckoutLinkPriceSelect: React.FC<CheckoutLinkPriceSelectProps> = ({
  product,
  value,
  onChange,
}) => {
  const pinnablePrices = useMemo(
    () => product?.prices.filter(isStaticPrice) ?? [],
    [product],
  )

  // Nothing meaningful to pick between — hide the picker.
  if (!product || pinnablePrices.length < 2) {
    return null
  }

  return (
    <Select
      value={value ?? AUTOMATIC_VALUE}
      onValueChange={(newValue) =>
        onChange(newValue === AUTOMATIC_VALUE ? null : newValue)
      }
    >
      <SelectTrigger>
        <SelectValue placeholder="Select a price" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={AUTOMATIC_VALUE}>
          Automatic (resolved at checkout)
        </SelectItem>
        {pinnablePrices.map((price) => (
          <SelectItem key={price.id} value={price.id}>
            {getPriceLabel(price, product)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export default CheckoutLinkPriceSelect
