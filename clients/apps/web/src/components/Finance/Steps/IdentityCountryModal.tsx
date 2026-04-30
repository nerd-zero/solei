'use client'

import { enums, schemas } from '@polar-sh/client'
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
import { useCallback } from 'react'
import { useForm } from 'react-hook-form'

interface IdentityCountryModalProps {
  defaultCountry?: string | null
  onSubmit: (country: schemas['UserUpdate']['country']) => void
  isLoading: boolean
}

export default function IdentityCountryModal({
  defaultCountry,
  onSubmit,
  isLoading,
}: IdentityCountryModalProps) {
  const form = useForm<{ country: schemas['UserUpdate']['country'] }>({
    defaultValues: {
      country:
        (defaultCountry as schemas['UserUpdate']['country']) ?? undefined,
    },
  })

  const handleSubmit = useCallback(
    (values: { country: schemas['UserUpdate']['country'] }) => {
      onSubmit(values.country)
    },
    [onSubmit],
  )

  return (
    <div className="flex flex-col gap-y-6 p-8">
      <Form {...form}>
        <form
          className="flex flex-col gap-y-4"
          onSubmit={form.handleSubmit(handleSubmit)}
        >
          <FormField
            control={form.control}
            name="country"
            rules={{ required: true }}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Country</FormLabel>
                <FormControl>
                  <CountryPicker
                    allowedCountries={enums.addressInputCountryValues}
                    value={field.value ?? undefined}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormDescription>
                  Select your country of residence. This determines the identity
                  verification method used.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            className="self-start"
            type="submit"
            loading={isLoading}
            disabled={isLoading}
          >
            Continue
          </Button>
        </form>
      </Form>
    </div>
  )
}
