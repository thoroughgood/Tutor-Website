import { useQuery } from "react-query"
import { HTTPProfileService } from "@/service/profileService"
import { Badge } from "./ui/badge"
import { MapPin } from "lucide-react"
import HeaderSeparator from "./headerSeparator"
import Link from "next/link"
import { Skeleton } from "./ui/skeleton"
import SmartAvatar from "./smartAvatar"

interface SmallProfileCard {
  id: string
  accountType: "tutor" | "student" // add more later if necessary
}
<<<<<<< HEAD

function FetchTutorData(id: string) {
  const { data } = useQuery({
    queryKey: ["students", id],
=======
const profileService = new HTTPProfileService()
export default function SmallProfileCard({
  id,
  accountType,
}: SmallProfileCard) {
  const { data } = useQuery({
    queryKey: [`${accountType}s`, id],
>>>>>>> main
    queryFn: async () => {
      return await profileService.getTutorProfile(id)
    },
  })
<<<<<<< HEAD
  return data
}

function FetchStudentData(id: string) {
  const { data } = useQuery({
    queryKey: ["students", id],
    queryFn: async () => {
      return await profileService.getStudentProfile(id)
    },
  })
  return data
}

const profileService = new HTTPProfileService()

export default function SmallProfileCard({
  id,
  accountType,
}: SmallProfileCard) {
  if (accountType === "tutor") {
    const data = FetchTutorData(id)
    return (
      <Link
        href={`/tutor/${id}`}
        className="flex w-screen max-w-md gap-5 rounded-md bg-background p-5 shadow transition hover:scale-[102%]"
      >
        <Avatar className="h-32 w-32 text-4xl ">
          {data ? (
            <>
              {data.profilePicture && <AvatarImage src={data.profilePicture} />}
              <AvatarFallback>
                {data.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </>
          ) : (
            <Skeleton className="h-full w-full" />
          )}
        </Avatar>
        <div className="flex grow flex-col justify-between">
          {data ? (
            <>
              <div className="flex flex-col items-center gap-2">
                <h2 className="w-full text-center text-2xl font-semibold text-foreground">
                  {data.name}
                </h2>
                <div className="flex items-center gap-4">
                  <Badge
                    variant="outline"
                    className="mt-1 border-muted-foreground px-3 py-1 text-xs text-muted-foreground"
                  >
                    TUTOR
                  </Badge>
                  {data.location && (
                    <div className="flex gap-1 text-muted-foreground">
                      <MapPin className="w-6" />
                      {data.location}
                    </div>
                  )}
                </div>
              </div>
              <HeaderSeparator>Course Offerings</HeaderSeparator>
              <div className=" flex flex-wrap justify-center gap-2">
                {data.courseOfferings.map((course) => (
                  <Badge variant="random" key={course}>
                    {course}
                  </Badge>
                ))}
              </div>
            </>
          ) : (
            <div className="space-y-2">
              <Skeleton className="h-10" />
              <div className="flex w-full gap-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
=======
  return (
    <Link
      href={`/tutor/${id}`}
      className="flex w-screen max-w-md gap-5 rounded-md bg-background p-5 shadow transition hover:scale-[102%]"
    >
      <SmartAvatar name={data?.name} profilePicture={data?.profilePicture} />
      <div className="flex grow flex-col justify-between">
        {data ? (
          <>
            <div className="flex flex-col items-center gap-2">
              <h2 className="w-full text-center text-2xl font-semibold text-foreground">
                {data.name}
              </h2>
              <div className="flex items-center gap-4">
                <Badge
                  variant="outline"
                  className="mt-1 border-muted-foreground px-3 py-1 text-xs text-muted-foreground"
                >
                  TUTOR
                </Badge>
                {data.location && (
                  <div className="flex gap-1 text-muted-foreground">
                    <MapPin className="w-6" />
                    {data.location}
                  </div>
                )}
>>>>>>> main
              </div>
            </div>
          )}
        </div>
      </Link>
    )
  } else if (accountType === "student") {
    const data = FetchStudentData(id)
    return (
      <Link
        href={`/student/${id}`}
        className="flex w-screen max-w-md gap-5 rounded-md bg-background p-5 shadow transition hover:scale-[102%]"
      >
        <Avatar className="h-32 w-32 text-4xl ">
          {data ? (
            <>
              {data.profilePicture && <AvatarImage src={data.profilePicture} />}
              <AvatarFallback>
                {data.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </>
          ) : (
            <Skeleton className="h-full w-full" />
          )}
        </Avatar>
        <div className="flex grow flex-col justify-between">
          {data ? (
            <>
              <div className="flex flex-col items-center gap-2">
                <h2 className="w-full text-center text-2xl font-semibold text-foreground">
                  {data.name}
                </h2>
                <div className="flex items-center gap-4">
                  <Badge
                    variant="outline"
                    className="mt-1 border-muted-foreground px-3 py-1 text-xs text-muted-foreground"
                  >
                    TUTOR
                  </Badge>
                  {data.location && (
                    <div className="flex gap-1 text-muted-foreground">
                      <MapPin className="w-6" />
                      {data.location}
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="space-y-2">
              <Skeleton className="h-10" />
              <div className="flex w-full gap-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            </div>
          )}
        </div>
      </Link>
    )
  }
}
