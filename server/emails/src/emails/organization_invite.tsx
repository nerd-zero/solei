import { Preview, Section, Text } from '@react-email/components'
import Button from '../components/Button'
import Footer from '../components/Footer'
import Intro from '../components/Intro'
import WrapperSolei from '../components/WrapperSolei'
import type { schemas } from '../types'

export function OrganizationInvite({
  email,
  organization_name,
  inviter_email,
  invite_url,
}: schemas['OrganizationInviteProps']) {
  return (
    <WrapperSolei>
      <Preview>You've been added to {organization_name} on Solei</Preview>
      <Intro>
        {inviter_email} has added you to{' '}
        <span className="font-bold">{organization_name}</span> on Solei.
      </Intro>
      <Section>
        <Text>
          As a member of {organization_name} you're now able to manage{' '}
          {organization_name}'s products, customers, and subscriptions on Solei.
        </Text>
      </Section>
      <Section className="text-center">
        <Button href={invite_url}>Go to the Solei dashboard</Button>
      </Section>
      <Footer email={email} />
    </WrapperSolei>
  )
}

OrganizationInvite.PreviewProps = {
  email: 'john@example.com',
  organization_name: 'Acme Inc.',
  inviter_email: 'admin@acme.com',
  invite_url: 'https://solei.to/dashboard/acme-inc',
}

export default OrganizationInvite
