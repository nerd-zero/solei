'use client'

import { setValidationErrors } from '@/utils/api/errors'
import { api } from '@/utils/client'
import { enums, isValidationError, schemas } from '@polar-sh/client'
import Button from '@polar-sh/ui/components/atoms/Button'
import CountryPicker from '@polar-sh/ui/components/atoms/CountryPicker'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@polar-sh/ui/components/ui/form'
import { useCallback, useState } from 'react'
import { useForm, useFormContext } from 'react-hook-form'
import PaystackBankAccountForm from './PaystackBankAccountForm'

const PAYSTACK_COUNTRIES = new Set(['ZA', 'GH', 'NG'])

const AccountCreateModal = ({
  forOrganizationId,
  returnPath,
}: {
  forOrganizationId: string
  returnPath: string
}) => {
  const form = useForm<{ country: string }>({
    defaultValues: { country: 'US' },
  })

  const {
    handleSubmit,
    setError,
    formState: { errors },
  } = form

  const [loading, setLoading] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState('US')
  const [verified, setVerified] = useState<
    schemas['BankAccountVerified'] | null
  >(null)
  const [bankFormValues, setBankFormValues] = useState<{
    account_number: string
    bank_code: string
    account_name: string
    account_type: string
    document_type: string
    document_number: string
  } | null>(null)

  const isPaystackCountry = PAYSTACK_COUNTRIES.has(selectedCountry)

  const goToOnboarding = useCallback(
    async (account: schemas['Account']) => {
      setLoading(true)
      const { data, error } = await api.POST(
        '/v1/accounts/{id}/onboarding_link',
        {
          params: {
            path: { id: account.id },
            query: { return_path: returnPath },
          },
        },
      )
      setLoading(false)

      if (error) {
        window.location.reload()
        return
      }

      window.location.href = data.url
    },
    [returnPath],
  )

  const createStripeAccount = useCallback(
    async (country: string) => {
      setLoading(true)

      const { data: account, error } = await api.POST('/v1/accounts', {
        body: {
          account_type: 'stripe',
          country:
            country as schemas['AccountCreateForOrganization']['country'],
          organization_id: forOrganizationId,
        },
      })

      if (error) {
        if (isValidationError(error.detail)) {
          setValidationErrors(error.detail, setError)
        } else {
          setError('root', { message: error.detail })
        }
        setLoading(false)
        return
      }

      setLoading(false)
      await goToOnboarding(account)
    },
    [forOrganizationId, goToOnboarding, setError],
  )

  const createPaystackAccount = useCallback(async () => {
    if (!bankFormValues) return
    setLoading(true)

    const { data: account, error } = await api.POST('/v1/accounts', {
      body: {
        account_type: 'paystack',
        country: selectedCountry as 'ZA' | 'GH' | 'NG',
        organization_id: forOrganizationId,
        bank_account: {
          account_number: bankFormValues.account_number,
          bank_code: bankFormValues.bank_code,
          account_name: bankFormValues.account_name || undefined,
          account_type: bankFormValues.account_type || undefined,
          document_type: bankFormValues.document_type || undefined,
          document_number: bankFormValues.document_number || undefined,
        },
      },
    })

    setLoading(false)

    if (error) {
      setError('root', {
        message:
          typeof error.detail === 'string' ? error.detail : 'An error occurred',
      })
      return
    }

    // Paystack accounts are ready immediately — no onboarding redirect
    window.location.reload()
    void account
  }, [bankFormValues, forOrganizationId, selectedCountry, setError])

  const onStripeSubmit = useCallback(
    async (data: { country: string }) => {
      await createStripeAccount(data.country)
    },
    [createStripeAccount],
  )

  return (
    <>
      <div className="flex flex-col gap-y-6 overflow-auto p-8">
        <h2>Setup payout account</h2>

        <Form {...form}>
          <form
            className="flex flex-col gap-y-4"
            onSubmit={handleSubmit(onStripeSubmit)}
          >
            <AccountCountry onCountryChange={setSelectedCountry} />

            {isPaystackCountry ? (
              <PaystackBankAccountForm
                country={selectedCountry as 'ZA' | 'GH' | 'NG'}
                verified={verified}
                isSubmitting={loading}
                onVerifying={(v) => setLoading(v)}
                onVerified={(v, values) => {
                  setVerified(v)
                  setBankFormValues(values)
                }}
                onSubmit={createPaystackAccount}
                onClearVerified={() => {
                  setVerified(null)
                  setBankFormValues(null)
                }}
              />
            ) : (
              <>
                {errors.root && (
                  <p className="text-destructive-foreground text-sm">
                    {errors.root.message}
                  </p>
                )}
                <Button
                  className="self-start"
                  type="submit"
                  loading={loading}
                  disabled={loading}
                >
                  Set up account
                </Button>
              </>
            )}
          </form>
        </Form>
      </div>
    </>
  )
}

const AccountCountry = ({
  onCountryChange,
}: {
  onCountryChange: (country: string) => void
}) => {
  const { control } = useFormContext<{ country: string }>()

  return (
    <>
      <FormField
        control={control}
        name="country"
        render={({ field }) => {
          return (
            <FormItem>
              <FormLabel>Country</FormLabel>
              <FormControl>
                <CountryPicker
                  value={field.value || undefined}
                  onChange={(v) => {
                    field.onChange(v)
                    onCountryChange(v ?? '')
                  }}
                  allowedCountries={[...enums.stripeAccountCountryValues, 'GH']}
                />
              </FormControl>
              <FormMessage />
              <FormDescription>
                If this is a personal account, please select your country of
                residence. If this is an organization or business, select the
                country of tax residency.
              </FormDescription>
            </FormItem>
          )
        }}
      />
    </>
  )
}

export default AccountCreateModal
