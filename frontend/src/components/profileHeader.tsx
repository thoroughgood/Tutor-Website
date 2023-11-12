import { Mail, MapPin, Phone } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"
import { Badge } from "./ui/badge"
import { cn } from "@/lib/utils"

interface ProfileHeaderProps {
  className?: string
  name: string
  accountType: string
  location: string | null
  phoneNumber: string | null
  email: string | null
  profilePicture?: string | null
}
/**
 * Reusable componenet for student/tutor profiles
 * Can handle NULL values for location, phoneNumber, email and profilePicture.
 */
export default function ProfileHeader({
  name,
  accountType,
  location,
  phoneNumber,
  email,
  profilePicture,
  className,
}: ProfileHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-10 md:flex-row",
        className,
      )}
    >
      <Avatar className="h-40 w-40 border-2 text-5xl ">
        {profilePicture && <AvatarImage src={profilePicture} />}
        <AvatarFallback>
          {name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col items-center gap-1 md:items-start">
        <h1 className="text-center text-3xl md:text-left">{name}</h1>
        <Badge
          variant="outline"
          className="mt-1 border-muted-foreground px-3 py-1 text-xs text-muted-foreground"
        >
          {accountType.toUpperCase()}
        </Badge>
        <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-1 md:justify-start">
          {location && (
            <FaintIconText>
              <MapPin />
              {location}
            </FaintIconText>
          )}
          {phoneNumber && (
            <FaintIconText>
              <Phone />
              {phoneNumber}
            </FaintIconText>
          )}
          {email && (
            <FaintIconText>
              <Mail />
              {email}
            </FaintIconText>
          )}
        </div>
      </div>
    </div>
  )
}

interface FaintIconTextProps {
  children: React.ReactNode
}
function FaintIconText({ children }: FaintIconTextProps) {
  return (
    <span className="flex items-center gap-1 text-muted-foreground [&>*:nth-child(1)]:w-5">
      {children}
    </span>
  )
}
