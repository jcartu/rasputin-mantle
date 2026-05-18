import type { Metadata } from 'next';
import { IBM_Plex_Mono } from 'next/font/google';
import { GeistSans } from 'geist/font/sans';
import './globals.css';
import { ThemeProvider } from '@/context/theme-context';
import { ToastProvider } from '@/components/ui/toast';

const ibmPlexMono = IBM_Plex_Mono({
  weight: ['400', '500', '600'],
  subsets: ['latin'],
  variable: '--font-ibm-plex-mono',
});

export const metadata: Metadata = {
  title: 'Rasputin Mantle',
  description: 'Self-hosted autonomous agent platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${GeistSans.variable} ${ibmPlexMono.variable} font-sans antialiased`}
        style={{
          backgroundColor: 'var(--color-background)',
          color: 'var(--color-foreground)',
          height: '100vh',
          width: '100vw',
          overflow: 'hidden',
          margin: 0,
        }}
      >
        <ThemeProvider>
          <ToastProvider>{children}</ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
