import useUser from "@/hooks/useUser"
import Image from "next/image"
import { Button } from "./ui/button"
import { LogOut, Menu } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

export default function Sidebar() {
  const { user } = useUser()
  const [isExpanded, setIsExpanded] = useState(false)
  return (
    <div>
      <Button
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute left-2 top-2 z-20 sm:hidden"
        variant={"ghost"}
      >
        <Menu />
      </Button>
      <div
        className={cn(
          "absolute right-0 z-10 flex h-full w-full flex-col justify-between gap-2 border bg-background p-4 shadow transition-all sm:static sm:w-52",
          {
            "right-full": !isExpanded,
          },
          "sm:right-0",
        )}
      >
        <div className="relative h-24">
          <Image src="/logo.svg" alt="logo" fill />
        </div>
        <div className="grow">test</div>
        <Button variant="ghost" className="flex justify-start gap-2">
          <LogOut className="h-4" />
          Logout
        </Button>
      </div>
    </div>
  )
}
