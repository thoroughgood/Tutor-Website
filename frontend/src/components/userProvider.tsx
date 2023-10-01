import { createContext, useState } from "react"

type UserTypes = "admin" | "tutor" | "student"
export type User = {
  userId: string
  userType: UserTypes
}
export interface UserContextType {
  user: User | null
  setUser: React.Dispatch<React.SetStateAction<User | null>>
}
export const UserContext = createContext<UserContextType | undefined>(undefined)

/**
 * Provides components rendered underneath it with useful user details
 */
export default function UserProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<User | null>(null)
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  )
}
