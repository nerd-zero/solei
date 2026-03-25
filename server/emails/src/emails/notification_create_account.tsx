import { Preview } from '@react-email/components'
import BodyText from '../components/BodyText'
import Button from '../components/Button'
import Footer from '../components/Footer'
import Intro from '../components/Intro'
import WrapperSolei from '../components/WrapperSolei'
import type { schemas } from '../types'

export function NotificationCreateAccount({
  organization_name,
  url,
}: schemas['MaintainerCreateAccountNotificationPayload']) {
  return (
    <WrapperSolei>
      <Preview>Your Solei account is being reviewed</Preview>
      <Intro>
        Now that you got your first payment to {organization_name}, you should
        create a payout account in order to receive your funds.
      </Intro>
      <BodyText>
        This operation only takes a few minutes and allows you to receive your
        money immediately.
      </BodyText>
      <Button href={url}>Create payout account</Button>

      <Footer email={null} />
    </WrapperSolei>
  )
}

NotificationCreateAccount.PreviewProps = {
  organization_name: 'Acme Inc.',
  url: 'https://solei.to',
}

export default NotificationCreateAccount
