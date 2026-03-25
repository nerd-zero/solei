import { Container } from '@react-email/components'
import SoleiHeader from './SoleiHeader'
import WrapperBase from './WrapperBase'

const WrapperSolei = ({ children }: { children: React.ReactNode }) => {
  return (
    <WrapperBase>
      <Container className="px-[12px] pt-[20px] pb-[10px]">
        <SoleiHeader />
      </Container>
      <Container className="px-[20px] pt-[10px] pb-[20px]">
        {children}
      </Container>
    </WrapperBase>
  )
}

export default WrapperSolei
