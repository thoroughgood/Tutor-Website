import { UserContext } from "@/components/userProvider"
import { useContext } from "react"

export default function useUser() {
  const userContext = useContext(UserContext)
  if (userContext === undefined) {
    throw new Error("useUser must only be used inside UserProvider")
  }
  return { ...userContext, signedIn: userContext.user !== null }
}
