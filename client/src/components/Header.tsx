import { FC } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const Header: FC = () => {
  const { t } = useTranslation();

  return (
    <header className="whatsapp-header">
      <h1>{t('title')}</h1>
      <div className="language-switcher">
        <LanguageSwitcher />
      </div>
    </header>
  );
};

export default Header;