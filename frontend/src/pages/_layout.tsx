import Sidebar from "@/components/sidebar"
import { ThemeToggle } from "@/components/themeToggle"
import useUser from "@/hooks/useUser"
import Image from "next/image"
import { useRouter } from "next/router"

interface LayoutProps {
  children: React.ReactNode
}
export default function Layout({ children }: LayoutProps) {
  const router = useRouter()
  const user = useUser()
  if (router.pathname.match(/register|login/i)) {
    return (
      <div className="flex h-screen w-screen">
        <ThemeToggle />
        <div className="grid w-full place-content-center">{children}</div>
        <Image
          src={"/blob-scene-haikei.svg"}
          alt="background"
          fill
          className="absolute bottom-0 -z-10 object-cover"
        />
      </div>
    )
  }

  if (!user.signedIn) {
    // TODO: uncomment when login is working
    // router.push("/login")
  }
  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar />
      {children}
    </div>
  )
}
