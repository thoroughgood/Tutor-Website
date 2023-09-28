import { useRouter } from "next/router"

interface LayoutProps {
  children: React.ReactNode
}
export default function Layout({ children }: LayoutProps) {
  const router = useRouter()
  if (router.pathname.match(/register|login/i)) {
    return (
      <div className="flex h-screen w-screen">
        <div className="grid w-full max-w-2xl place-content-center border shadow">
          {children}
        </div>
      </div>
    )
  }
  return (
    <div className="flex h-screen w-screen p-5 hover:font-bold hover:text-red-500">
      {children}
    </div>
  )
}
