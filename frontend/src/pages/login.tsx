import { Button } from "@/components/ui/button"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"

export default function Login() {
  const router = useRouter()
  const { setUser } = useUser()
  return (
    <Button
      onClick={() => {
        setUser({ userId: "1337", userType: "tutor" })
        router.push("/dashboard")
      }}
    >
      Fake login
    </Button>
  )
}
