export default function EmbedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="embed-wrapper bg-white">
      {children}
    </div>
  )
}
