import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MockProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import { useQuery } from "react-query"

const profileService = new MockProfileService()
export default function TutorProfile() {
  const router = useRouter()
  const tutorId = router.query.tutorId as string
  const { data } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: () => profileService.getTutorProfile(tutorId),
  })

  return (
    <div className="p-12">
      <div className="flex">
        <Avatar className="h-40 w-40 text-5xl">
          {data?.profilePicture && <AvatarImage src={data.profilePicture} />}
          <AvatarFallback>
            {data?.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
  )
}
