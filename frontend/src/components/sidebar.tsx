import useUser from "@/hooks/useUser"
import Image from "next/image"
import { Button } from "./ui/button"
import {
  Calendar,
  FileQuestion,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Search,
  User,
} from "lucide-react"
import { cn, toastProtectedFnCall } from "@/lib/utils"
import { useState } from "react"
import Link from "next/link"
import { HTTPAuthService } from "@/service/authService"
import { useRouter } from "next/router"

export default function Sidebar() {
  const authService = new HTTPAuthService()
  const router = useRouter()
  const { user, setUser } = useUser()
  const [isExpanded, setIsExpanded] = useState(false)
  return (
    <div>
      <Button
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute left-2 top-2 z-30 sm:hidden"
        variant={"ghost"}
      >
        <Menu />
      </Button>
      <div
        className={cn(
          "absolute right-0 z-20 flex h-full w-full flex-col justify-between gap-2 border bg-background p-4 shadow transition-all sm:static sm:w-52",
          {
            "right-full": !isExpanded,
          },
          "sm:right-0",
        )}
      >
        <div className="relative h-24">
          <Image src="/logo.svg" alt="logo" fill />
        </div>
        <div className="flex grow flex-col gap-1 text-muted-foreground">
          {user?.userType === "student" ? (
            <StudentLinks />
          ) : user?.userType === "tutor" ? (
            <TutorLinks />
          ) : (
            <AdminLinks />
          )}
        </div>

        <Button
          variant="ghost"
          className="flex justify-start gap-2 text-muted-foreground"
          onClick={async () => {
            // idk why you have to put authService.logout as an
            // anonymous function but you do otherwise undefined error
            if (await toastProtectedFnCall(() => authService.logout())) {
              setUser(null)
              router.push("/login")
            }
          }}
        >
          <LogOut className="h-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}

function TutorLinks() {
  const { user } = useUser()
  return (
    <>
      <SidebarLink href="/appointments">
        <Calendar />
        Appointments
      </SidebarLink>
      <SidebarLink href="/requests">
        <FileQuestion />
        Requests
      </SidebarLink>
      <SidebarLink href="/messages">
        <MessageSquare />
        Messages
      </SidebarLink>
      <SidebarLink href={`/tutor/${user?.userId}`}>
        <User />
        Profile
      </SidebarLink>
    </>
  )
}

function StudentLinks() {
  const { user } = useUser()
  return (
    <>
      <SidebarLink href={"/appointments"}>
        <Calendar />
        Appointments
      </SidebarLink>
      <SidebarLink href="/findTutor">
        <Search />
        Find Tutors
      </SidebarLink>
      <SidebarLink href="/messages">
        <MessageSquare />
        Messages
      </SidebarLink>
      <SidebarLink href={`/student/${user?.userId}`}>
        <User />
        Profile
      </SidebarLink>
    </>
  )
}

function AdminLinks() {
  const { user } = useUser()

  return (
    <>
      <SidebarLink href={"/create"}>
        <Plus strokeWidth={1.75} /> Admin Generator
      </SidebarLink>
      <SidebarLink href="/findUser">
        <Search />
        Find Users
      </SidebarLink>
    </>
  )
}

interface SidebarLinkProps {
  href: string
  children: React.ReactNode
}
function SidebarLink({ href, children }: SidebarLinkProps) {
  return (
    <Button asChild variant="ghost" className="flex justify-start gap-2">
      <Link href={href} className="[&>svg]:h-5">
        {children}
      </Link>
    </Button>
  )
}
