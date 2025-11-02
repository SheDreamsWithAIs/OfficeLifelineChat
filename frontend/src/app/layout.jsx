import './globals.css'

export const metadata = {
  title: 'Office Lifeline Chat',
  description: 'Multi-agent customer service chat',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

