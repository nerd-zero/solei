import { Img, Section } from "@react-email/components";

interface HeaderProps {}

const Header = () => (
  <Section>
    <div className="relative h-[48px]">
      <Img
        alt="Solei Logo"
        height="48"
        src="https://public.solei.to/emails/solei-logo-black-badge.png"
      />
    </div>
  </Section>
);

export default Header;
