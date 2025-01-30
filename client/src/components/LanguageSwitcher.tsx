import { useTranslation } from 'react-i18next';
import { GB as GBFlag } from 'country-flag-icons/react/3x2';
import { BR as BRFlag } from 'country-flag-icons/react/3x2';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  return (
    <div className="language-switcher">
      <button
        onClick={() => i18n.changeLanguage('en')}
        className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
      >
        <GBFlag className="flag" />
        <span>EN</span>
      </button>
      <button
        onClick={() => i18n.changeLanguage('pt')}
        className={`lang-btn ${i18n.language === 'pt' ? 'active' : ''}`}
      >
        <BRFlag className="flag" />
        <span>PT</span>
      </button>
    </div>
  );
};

export default LanguageSwitcher;
