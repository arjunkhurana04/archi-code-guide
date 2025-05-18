import { Translator } from 'components/i18n';

import 'assets/logo_dark.svg';
import LogoDark from 'assets/logo_dark.svg?react';
import 'assets/logo_light.svg';
import LogoLight from 'assets/logo_light.svg?react';

import { useTheme } from './ThemeProvider';

export default function WaterMark() {
  const { variant } = useTheme();
  const Logo = variant === 'light' ? LogoLight : LogoDark;

  return (
    <div className="watermark-container" style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      opacity: 0.9,
    }}>
      <Logo style={{ height: '3rem', marginBottom: '0.25rem' }} />
      <p style={{
        fontSize: '1rem',
        fontWeight: 400,
        margin: '0',
        opacity: 0.75,
        letterSpacing: '0',
      }}>
        Built by Arjun Khurana
      </p>
    </div>
  );
}