import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GUARD Dashboard - CPP Donggi',
  description: 'Generative Understanding for Anomaly Response & Detection',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-100">{children}</body>
    </html>
  );
}
