'use client'

import AccountCreateModal from '@/components/Accounts/AccountCreateModal'
import AccountStep from '@/components/Finance/Steps/AccountStep'
import IdentityCountryModal from '@/components/Finance/Steps/IdentityCountryModal'
import IdentityStep from '@/components/Finance/Steps/IdentityStep'
import PaystackIdentityModal from '@/components/Finance/Steps/PaystackIdentityModal'
import { DashboardBody } from '@/components/Layout/DashboardLayout'
import { Modal } from '@/components/Modal'
import { useModal } from '@/components/Modal/useModal'
import AIValidationResult from '@/components/Organization/AIValidationResult'
import OrganizationProfileSettings from '@/components/Settings/OrganizationProfileSettings'
import { Section, SectionDescription } from '@/components/Settings/Section'
import { useAuth } from '@/hooks'
import { useOrganizationAccount } from '@/hooks/queries'
import { useOrganizationReviewStatus } from '@/hooks/queries/org'
import { useIdentityVerification } from '@/hooks/useIdentityVerification'
import { api } from '@/utils/client'
import { ClientResponseError, schemas, unwrap } from '@polar-sh/client'
import { CheckIcon } from 'lucide-react'
import React, { useCallback, useEffect, useState } from 'react'

export default function ClientPage({
  organization,
}: {
  organization: schemas['Organization']
}) {
  const { currentUser, reloadUser } = useAuth()
  const {
    isShown: isShownSetupModal,
    show: showSetupModal,
    hide: hideSetupModal,
  } = useModal()

  const [requireDetails, setRequireDetails] = useState(
    !organization.details_submitted_at,
  )
  const identityVerificationStatus = currentUser?.identity_verification_status

  const { data: organizationAccount, error: accountError } =
    useOrganizationAccount(organization.id)
  const { data: reviewStatus } = useOrganizationReviewStatus(organization.id)

  const isNotAdmin =
    accountError &&
    (accountError as ClientResponseError)?.response?.status === 403

  const isApproved =
    reviewStatus?.verdict === 'PASS' ||
    reviewStatus?.appeal_decision === 'approved'

  const {
    showCountryPicker,
    openCountryPicker,
    closeCountryPicker,
    isUpdatingCountry,
    paystackData,
    clearPaystackData,
    startVerificationWithCountry,
    startPolling,
    clearPollingOnStatusChange,
    stopPolling,
  } = useIdentityVerification(identityVerificationStatus, reloadUser)

  useEffect(() => {
    clearPollingOnStatusChange()
  }, [clearPollingOnStatusChange])

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  const handlePaystackSuccess = useCallback(() => {
    clearPaystackData()
    startPolling()
  }, [clearPaystackData, startPolling])

  const handleDetailsSubmitted = useCallback(() => {
    setRequireDetails(false)
  }, [])

  const handleStartAccountSetup = useCallback(async () => {
    if (!organizationAccount || !organizationAccount.stripe_id) {
      showSetupModal()
    } else {
      const link = await unwrap(
        api.POST('/v1/accounts/{id}/onboarding_link', {
          params: {
            path: { id: organizationAccount.id },
            query: {
              return_path: `/dashboard/${organization.slug}/finance/account`,
            },
          },
        }),
      )
      window.location.href = link.url
    }
  }, [organization.slug, organizationAccount, showSetupModal])

  return (
    <DashboardBody wrapperClassName="max-w-(--breakpoint-sm)!">
      <div className="flex flex-col gap-y-12">
        <Section>
          <SectionDescription
            title="Account Review"
            description={
              requireDetails
                ? 'Tell us about your organization so we can review the usecase.'
                : 'Your submitted organization details and compliance status.'
            }
          />
          {requireDetails ? (
            <OrganizationProfileSettings
              organization={organization}
              kyc={true}
              onSubmitted={handleDetailsSubmitted}
            />
          ) : isApproved ? (
            <div className="dark:bg-polar-800 rounded-2xl border bg-white p-8 text-center">
              <span className="dark:bg-polar-700 mb-3 inline-flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
                <CheckIcon className="dark:text-polar-400 h-4 w-4 text-gray-500" />
              </span>
              <h4 className="mb-2 font-medium">Account approved</h4>
              <p className="dark:text-polar-400 mx-auto max-w-sm text-sm text-balance text-gray-600">
                Your product and organization details have been reviewed and
                approved.
              </p>
            </div>
          ) : (
            <AIValidationResult organization={organization} />
          )}
        </Section>

        <Section>
          <SectionDescription
            title="Payout Account"
            description="Set up your payout account to receive payouts."
          />
          {!isApproved ? (
            <InfoCard>Please go through account review first</InfoCard>
          ) : isNotAdmin ? (
            <InfoCard>This can only be done by the organization admin</InfoCard>
          ) : (
            <AccountStep
              organizationAccount={organizationAccount}
              isNotAdmin={false}
              onStartAccountSetup={handleStartAccountSetup}
            />
          )}
        </Section>

        <Section>
          <SectionDescription
            title="Identity Verification"
            description="Verify your identity to comply with financial regulations."
          />
          {isApproved ? (
            <IdentityStep
              identityVerificationStatus={identityVerificationStatus}
              onStartIdentityVerification={openCountryPicker}
            />
          ) : (
            <InfoCard>Please go through account review first</InfoCard>
          )}
        </Section>

        <Modal
          title="Create Payout Account"
          isShown={isShownSetupModal}
          className="min-w-[400px]"
          hide={hideSetupModal}
          modalContent={
            <AccountCreateModal
              forOrganizationId={organization.id}
              returnPath={`/dashboard/${organization.slug}/finance/account`}
            />
          }
        />

        <Modal
          title="Select Your Country"
          isShown={showCountryPicker}
          className="min-w-[400px]"
          hide={closeCountryPicker}
          modalContent={
            <IdentityCountryModal
              defaultCountry={currentUser?.country}
              onSubmit={startVerificationWithCountry}
              isLoading={isUpdatingCountry}
            />
          }
        />

        <Modal
          title="Verify Your Identity"
          isShown={!!paystackData}
          className="min-w-[400px]"
          hide={clearPaystackData}
          modalContent={
            paystackData && (
              <PaystackIdentityModal
                customerCode={paystackData.customerCode}
                requiredIdType={paystackData.requiredIdType}
                firstName={currentUser?.first_name ?? ''}
                lastName={currentUser?.last_name ?? ''}
                onSuccess={handlePaystackSuccess}
                onCancel={clearPaystackData}
              />
            )
          }
        />
      </div>
    </DashboardBody>
  )
}

function InfoCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="dark:bg-polar-800 rounded-2xl bg-gray-100 p-5 text-center">
      <p className="dark:text-polar-500 text-sm text-gray-500">{children}</p>
    </div>
  )
}
