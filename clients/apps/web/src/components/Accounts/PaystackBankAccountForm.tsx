'use client'

import { schemas } from '@polar-sh/client'
import Button from '@polar-sh/ui/components/atoms/Button'
import Input from '@polar-sh/ui/components/atoms/Input'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@polar-sh/ui/components/ui/form'
import { useCallback, useState } from 'react'
import { useForm } from 'react-hook-form'
import ZABankFields from './ZABankFields'

export type BankFormValues = {
  account_number: string
  bank_code: string
  account_name: string
  account_type: string
  document_type: string
  document_number: string
}

type Props = {
  country: 'ZA' | 'GH' | 'NG'
  onVerified: (
    verified: schemas['BankAccountVerified'],
    formValues: BankFormValues,
  ) => void
  onVerifying: (loading: boolean) => void
  isSubmitting: boolean
  verified: schemas['BankAccountVerified'] | null
  onSubmit: () => void
  onClearVerified: () => void
}

export default function PaystackBankAccountForm({
  country,
  onVerified,
  onVerifying,
  isSubmitting,
  verified,
  onSubmit,
  onClearVerified,
}: Props) {
  const isZA = country === 'ZA'
  const [verifyError, setVerifyError] = useState<string | null>(null)
  const [isVerifying, setIsVerifying] = useState(false)

  const form = useForm<BankFormValues>({
    defaultValues: {
      account_number: '',
      bank_code: '',
      account_name: '',
      account_type: 'personal',
      document_type: 'identityNumber',
      document_number: '',
    },
  })

  const handleVerify = useCallback(
    async (values: BankFormValues) => {
      setVerifyError(null)
      setIsVerifying(true)
      onVerifying(true)

      const { api } = await import('@/utils/client')
      const { data, error } = await api.POST('/v1/accounts/verify-bank', {
        body: {
          country: country as 'ZA' | 'GH' | 'NG',
          bank_account: {
            account_number: values.account_number,
            bank_code: values.bank_code,
            account_name: isZA ? values.account_name : undefined,
            account_type: isZA ? values.account_type : undefined,
            document_type: isZA ? values.document_type : undefined,
            document_number: isZA
              ? values.document_number || undefined
              : undefined,
          },
        },
      })

      setIsVerifying(false)
      onVerifying(false)

      if (error) {
        setVerifyError(
          typeof error.detail === 'string'
            ? error.detail
            : 'Failed to verify bank account.',
        )
        return
      }

      onVerified(data, values)
    },
    [country, isZA, onVerified, onVerifying],
  )

  if (verified) {
    return (
      <div className="flex flex-col gap-y-4">
        <div className="dark:bg-polar-800 rounded-xl border border-green-200 bg-green-50 p-4 dark:border-green-800">
          <p className="text-sm font-medium text-green-700 dark:text-green-400">
            Account verified
          </p>
          <p className="text-sm text-green-600 dark:text-green-500">
            {verified.account_name} ({verified.account_number})
          </p>
        </div>
        <div className="flex gap-x-2">
          <Button
            type="button"
            loading={isSubmitting}
            disabled={isSubmitting}
            onClick={onSubmit}
          >
            Set up account
          </Button>
          <Button
            type="button"
            variant="ghost"
            disabled={isSubmitting}
            onClick={onClearVerified}
          >
            Change details
          </Button>
        </div>
      </div>
    )
  }

  return (
    <Form {...form}>
      <form
        className="flex flex-col gap-y-4"
        onSubmit={form.handleSubmit(handleVerify)}
      >
        <FormField
          control={form.control}
          name="account_number"
          rules={{ required: 'Account number is required' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Account Number</FormLabel>
              <FormControl>
                <Input {...field} placeholder="0001234567" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bank_code"
          rules={{ required: 'Bank code is required' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bank Code</FormLabel>
              <FormControl>
                <Input {...field} placeholder="058" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {isZA && <ZABankFields />}

        {verifyError && (
          <p className="text-destructive-foreground text-sm">{verifyError}</p>
        )}

        <Button
          className="self-start"
          type="submit"
          loading={isVerifying}
          disabled={isVerifying}
        >
          Verify Account
        </Button>
      </form>
    </Form>
  )
}
