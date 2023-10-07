import useUser from "@/hooks/useUser"
import Image from "next/image"
import { Button } from "./ui/button"
import {
  Calendar,
  FileQuestion,
  LogOut,
  Menu,
  MessageSquare,
  Search,
  User,
} from "lucide-react"
import { cn, toastProtectedFnCall } from "@/lib/utils"
import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/router"
import { HTTPAuthService } from "@/service/authService"

const authService = new HTTPAuthService()
export default function Sidebar() {
  const { user, signedIn } = useUser()
  const router = useRouter()
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
          {user?.userType === "tutor" ? <StudentLinks /> : <TutorLinks />}
        </div>
        <Button
          variant="ghost"
          className="flex justify-start gap-2 text-muted-foreground"
          onClick={() => toastProtectedFnCall(authService.logout)}
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
