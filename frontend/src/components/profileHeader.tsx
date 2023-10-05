import { Mail, MapPin, Phone } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"

interface ProfileHeaderProps {
  name: string
  accountType: string
  location?: string
  phoneNumber?: string
  email?: string
  profilePicture: string
}
export default function ProfileHeader({
  name,
  accountType,
  location,
  phoneNumber,
  email,
  profilePicture,
}: ProfileHeaderProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-10 md:flex-row">
      <Avatar className="h-40 w-40 text-5xl">
        {profilePicture && <AvatarImage src={profilePicture} />}
        <AvatarFallback className="border-2">
          {name
            .split(" ")
            .map((n) => n[0])
            .join("")}
        </AvatarFallback>
      </Avatar>
      <div>
        <div className="">
          <h1 className="text-center text-2xl md:text-left">{name}</h1>
          <h2 className="text-center font-bold md:text-left">{accountType}</h2>
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
