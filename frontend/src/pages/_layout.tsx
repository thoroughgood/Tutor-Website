import { ThemeToggle } from "@/components/themeToggle"
import { useRouter } from "next/router"

interface LayoutProps {
  children: React.ReactNode
}
export default function Layout({ children }: LayoutProps) {
  const router = useRouter()
  if (router.pathname.match(/register|login/i)) {
    return (
      <div className="flex h-screen w-screen bg-background">
        <ThemeToggle />
        <div className="grid w-full place-content-center ">{children}</div>
      </div>
    )
  }
  return <div className="flex h-screen w-screen">{children}</div>
}
