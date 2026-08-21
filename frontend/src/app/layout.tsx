import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Dental Clinic',
  description: 'Hệ thống đặt lịch nha khoa',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  )
}
