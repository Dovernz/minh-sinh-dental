import Header from '@/components/Header'
import Footer from '@/components/Footer'

async function getMenus() {
  try {
    const res = await fetch('http://backend:8000/api/menus/', { next: { revalidate: 60 } })
    if (!res.ok) return []
    return res.json()
  } catch (error) {
    console.error("Failed to fetch menus:", error)
    return []
  }
}

export default async function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const menus = await getMenus()

  return (
    <>
      <Header menus={menus} />
      {children}
      <Footer />
    </>
  )
}
