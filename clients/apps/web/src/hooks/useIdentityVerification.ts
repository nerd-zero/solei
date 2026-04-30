'use client'

import { toast } from '@/components/Toast/use-toast'
import { useCreateIdentityVerification, useUpdateUser } from '@/hooks/queries'
import { schemas } from '@polar-sh/client'
import { loadStripe } from '@stripe/stripe-js'
import { useCallback, useRef, useState } from 'react'

interface PaystackVerificationData {
  customerCode: string
  requiredIdType: string | null | undefined
}

export function useIdentityVerification(
  identityVerificationStatus: string | undefined,
  reloadUser: () => Promise<unknown>,
) {
  const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY || '')
  const createIdentityVerification = useCreateIdentityVerification()
  const updateUser = useUpdateUser()
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const pollingInitialStatusRef = useRef<string | undefined | null>(null)
  const [showCountryPicker, setShowCountryPicker] = useState(false)
  const [paystackData, setPaystackData] =
    useState<PaystackVerificationData | null>(null)

  const startPolling = useCallback(() => {
    pollingInitialStatusRef.current = identityVerificationStatus
    reloadUser()
    pollingRef.current = setInterval(async () => {
      await reloadUser()
    }, 3000)
    setTimeout(() => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }, 30_000)
  }, [identityVerificationStatus, reloadUser])

  const clearPollingOnStatusChange = useCallback(() => {
    if (
      pollingRef.current &&
      identityVerificationStatus !== pollingInitialStatusRef.current
    ) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [identityVerificationStatus])

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
    }
  }, [])

  const openCountryPicker = useCallback(() => setShowCountryPicker(true), [])
  const closeCountryPicker = useCallback(() => setShowCountryPicker(false), [])

  const startVerificationWithCountry = useCallback(
    async (country: schemas['UserUpdate']['country']) => {
      const { error: updateError } = await updateUser.mutateAsync({ country })
      if (updateError) {
        toast({
          title: 'Error saving country',
          description: 'Unable to save your country. Please try again.',
        })
        return
      }

      setShowCountryPicker(false)

      let result: Awaited<
        ReturnType<typeof createIdentityVerification.mutateAsync>
      >
      try {
        result = await createIdentityVerification.mutateAsync()
      } catch {
        toast({
          title: 'Network error',
          description: 'Unable to reach the server. Please try again.',
        })
        return
      }

      const { data, error } = result
      if (error) {
        const errorBody = error as Record<string, unknown>
        const errorDetail = errorBody.detail as
          | string
          | { error?: string; detail?: string }
          | undefined
        if (
          (typeof errorDetail === 'object' &&
            errorDetail?.error === 'IdentityVerificationProcessing') ||
          errorDetail === 'Your identity verification is still processing.'
        ) {
          toast({
            title: 'Identity verification in progress',
            description:
              'Your identity verification is already being processed. Please wait for it to complete.',
          })
        } else {
          toast({
            title: 'Error starting identity verification',
            description:
              typeof errorDetail === 'string'
                ? errorDetail
                : (typeof errorDetail === 'object' && errorDetail?.detail) ||
                  'Unable to start identity verification. Please try again.',
          })
        }
        return
      }

      if (data?.provider === 'paystack') {
        setPaystackData({
          customerCode: data.customer_code ?? '',
          requiredIdType: data.required_id_type,
        })
        return
      }

      const stripe = await stripePromise
      if (!stripe) {
        toast({
          title: 'Error loading Stripe',
          description:
            'Unable to load identity verification. Please try again.',
        })
        return
      }
      const { error: stripeError } = await stripe.verifyIdentity(
        data?.client_secret ?? '',
      )
      if (stripeError) {
        toast({
          title: 'Identity verification error',
          description:
            stripeError.message ||
            'Something went wrong during verification. Please try again.',
        })
        return
      }
      startPolling()
    },
    [createIdentityVerification, updateUser, stripePromise, startPolling],
  )

  const clearPaystackData = useCallback(() => setPaystackData(null), [])

  return {
    showCountryPicker,
    openCountryPicker,
    closeCountryPicker,
    isUpdatingCountry: updateUser.isPending,
    paystackData,
    clearPaystackData,
    startVerificationWithCountry,
    startPolling,
    clearPollingOnStatusChange,
    stopPolling,
  }
}
