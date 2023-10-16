import { HTTPAuthService } from "@/service/authService"
import { createContext, useEffect, useState } from "react"
import { z } from "zod"

type UserTypes = "admin" | "tutor" | "student"
export type User = {
  userId: string
  userType: UserTypes
}
export interface UserContextType {
  user: User | null
  checkingUser: boolean
  setUser: React.Dispatch<React.SetStateAction<User | null>>
}
export const UserContext = createContext<UserContextType | undefined>(undefined)

const validator = z.object({
  userId: z.string(),
  userType: z.enum(["admin", "tutor", "student"]),
})

/**
 * Provides components rendered underneath it with useful user details
 */
const authService = new HTTPAuthService()
export default function UserProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<User | null>(null)
  const [checkingUser, setCheckingUser] = useState(true)
  useEffect(() => {
    ;(async () => {
      try {
        const { id, accountType } = await authService.checkUser()
        setUser({
          userId: id,
          userType: accountType,
        })
      } catch {
        console.log("User is not logged in")
      }
      setCheckingUser(false)
    })()
  }, [])
  return (
    <UserContext.Provider value={{ user, setUser, checkingUser }}>
      {children}
    </UserContext.Provider>
  )
}
