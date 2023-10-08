interface HeaderSeparatorProps {
  children: React.ReactNode
}
export default function HeaderSeparator({ children }: HeaderSeparatorProps) {
  return (
    <div className="relative flex justify-center">
      <hr className="absolute top-1/2 w-full" />
      <h2 className="z-10 bg-background px-2">{children}</h2>
    </div>
  )
}
