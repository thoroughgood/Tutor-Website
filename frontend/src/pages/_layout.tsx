import Sidebar from "@/components/sidebar"
import { ThemeToggle } from "@/components/themeToggle"
import useUser from "@/hooks/useUser"
import { Loader2 } from "lucide-react"
import Image from "next/image"
import { useRouter } from "next/router"
import { useEffect } from "react"
import { Toaster } from "react-hot-toast"

interface LayoutProps {
  children: React.ReactNode
}
export default function Layout({ children }: LayoutProps) {
  const router = useRouter()
  const { signedIn, checkingUser } = useUser()
  useEffect(() => {
    if (checkingUser) {
      return
    }
    if (!signedIn && !router.pathname.match(/register|login/i)) {
      router.push("/login")
    }
    if (router.pathname.match(/register|login/i) && signedIn) {
      router.push("/dashboard")
    }
  }, [signedIn, router, checkingUser])

  if (checkingUser) {
    return (
      <div className="grid h-screen w-screen place-content-center">
        <Loader2 className="h-10 w-10 animate-spin" />
      </div>
    )
  }
  if (router.pathname.match(/register|login/i)) {
    return (
      <div className="flex h-screen w-screen">
        <Toaster />
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

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Toaster />
      <Sidebar />
      <div className="h-full w-full overflow-hidden">{children}</div>
    </div>
  )
}
