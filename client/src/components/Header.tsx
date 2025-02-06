import { FC } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import recapLogo from '../assets/recap_logo.png';

const Header: FC = () => {
  const { t } = useTranslation();

  return (
    <header className="whatsapp-header">
      <div className="header-content">
        <img src={recapLogo} alt="Recap Logo" className="header-logo" />
        <h1>{t('title')}</h1>
      </div>
      <div className="language-switcher">
        <LanguageSwitcher />
      </div>
    </header>
  );
};

export default Header;