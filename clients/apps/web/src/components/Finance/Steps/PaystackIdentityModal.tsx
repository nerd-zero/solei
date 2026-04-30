'use client'

import { toast } from '@/components/Toast/use-toast'
import { useSubmitPaystackIdentityVerification } from '@/hooks/queries'
import { schemas } from '@polar-sh/client'
import Button from '@polar-sh/ui/components/atoms/Button'
import Input from '@polar-sh/ui/components/atoms/Input'
import { useCallback } from 'react'
import { useForm } from 'react-hook-form'

interface PaystackIdentityModalProps {
  customerCode: string
  requiredIdType: string | null | undefined
  firstName: string
  lastName: string
  onSuccess: () => void
  onCancel: () => void
}

type FormValues = {
  id_number: string
  first_name: string
  last_name: string
  bvn?: string
  bank_code?: string
  account_number?: string
}

const ID_TYPE_LABELS: Record<string, string> = {
  sa_id: 'South African ID Number',
  tin: 'TIN (Tax Identification Number)',
  bank_account: 'Bank Account Number',
}

export default function PaystackIdentityModal({
  requiredIdType,
  firstName,
  lastName,
  onSuccess,
  onCancel,
}: PaystackIdentityModalProps) {
  const idType = (requiredIdType ??
    'bank_account') as schemas['PaystackIdentitySubmit']['id_type']
  const submitVerification = useSubmitPaystackIdentityVerification()

  const { register, handleSubmit, formState } = useForm<FormValues>({
    defaultValues: { first_name: firstName, last_name: lastName },
  })

  const onSubmit = useCallback(
    async (values: FormValues) => {
      const { error } = await submitVerification.mutateAsync({
        id_type: idType,
        id_number: values.id_number,
        first_name: values.first_name,
        last_name: values.last_name,
        ...(idType === 'bank_account'
          ? {
              bvn: values.bvn,
              bank_code: values.bank_code,
              account_number: values.account_number,
            }
          : {}),
      })
      if (error) {
        const detail = (error as Record<string, unknown>).detail
        toast({
          title: 'Verification failed',
          description:
            typeof detail === 'string'
              ? detail
              : 'Unable to submit verification. Please try again.',
        })
        return
      }
      toast({
        title: 'Verification submitted',
        description: 'Your identity verification is being processed.',
      })
      onSuccess()
    },
    [idType, submitVerification, onSuccess],
  )

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-y-4 p-6"
    >
      <p className="dark:text-polar-400 text-sm text-gray-500">
        Please provide your {ID_TYPE_LABELS[idType] ?? 'ID'} to verify your
        identity.
      </p>

      <div className="flex flex-col gap-y-1">
        <label className="text-sm font-medium">First Name</label>
        <Input {...register('first_name', { required: true })} />
      </div>

      <div className="flex flex-col gap-y-1">
        <label className="text-sm font-medium">Last Name</label>
        <Input {...register('last_name', { required: true })} />
      </div>

      <div className="flex flex-col gap-y-1">
        <label className="text-sm font-medium">
          {ID_TYPE_LABELS[idType] ?? 'ID Number'}
        </label>
        <Input {...register('id_number', { required: true })} />
      </div>

      {idType === 'bank_account' && (
        <>
          <div className="flex flex-col gap-y-1">
            <label className="text-sm font-medium">BVN</label>
            <Input
              {...register('bvn')}
              placeholder="Bank Verification Number"
            />
          </div>
          <div className="flex flex-col gap-y-1">
            <label className="text-sm font-medium">Bank Code</label>
            <Input {...register('bank_code')} />
          </div>
          <div className="flex flex-col gap-y-1">
            <label className="text-sm font-medium">Account Number</label>
            <Input {...register('account_number')} />
          </div>
        </>
      )}

      <div className="flex gap-x-3 pt-2">
        <Button
          type="submit"
          disabled={formState.isSubmitting}
          className="flex-1"
        >
          {formState.isSubmitting ? 'Submitting...' : 'Submit'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </form>
  )
}
