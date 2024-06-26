import { useQuery } from "react-query"
import {
  HTTPProfileService,
  StudentProfile,
  TutorProfile,
} from "@/service/profileService"
import { Badge } from "./ui/badge"
import { MapPin, Star } from "lucide-react"
import HeaderSeparator from "./headerSeparator"
import Link from "next/link"
import { Skeleton } from "./ui/skeleton"
import SmartAvatar from "./smartAvatar"

interface SmallProfileCard {
  id: string
  accountType: "tutor" | "student" // add more later if necessary
}

const profileService = new HTTPProfileService()

export default function SmallProfileCard({
  id,
  accountType,
}: SmallProfileCard) {
  const { data } = useQuery({
    queryKey: [`${accountType}s`, id],
    queryFn: async (): Promise<StudentProfile | TutorProfile | undefined> => {
      if (accountType === "student") {
        return await profileService.getStudentProfile(id)
      } else if (accountType === "tutor") {
        return await profileService.getTutorProfile(id)
      }
    },
  })

  return (
    <Link
      href={`/${accountType}/${id}`}
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
                {accountType === "tutor" &&
                  (data as TutorProfile).rating >= 0 && (
                    <div className="mt-1 flex flex-row gap-1">
                      <div>
                        <Star fill="gold" color="gold" className="w-4" />
                      </div>
                      <div>
                        {Math.round((data as TutorProfile).rating * 10) / 10}/5
                      </div>
                    </div>
                  )}
                <Badge
                  variant="outline"
                  className="mt-1 border-muted-foreground px-3 py-1 text-xs text-muted-foreground"
                >
                  {accountType.toUpperCase()}
                </Badge>

                {data.location && (
                  <div className="flex gap-1 text-muted-foreground">
                    <MapPin className="w-6" />
                    {data.location}
                  </div>
                )}
              </div>
            </div>
            {accountType === "tutor" &&
              (data as TutorProfile).courseOfferings.length > 0 && (
                <>
                  <HeaderSeparator>Course Offerings</HeaderSeparator>
                  <div className="flex flex-wrap justify-center gap-2">
                    {(data as TutorProfile).courseOfferings.map((course) => (
                      <Badge variant="random" key={course}>
                        {course}
                      </Badge>
                    ))}
                  </div>
                </>
              )}
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
