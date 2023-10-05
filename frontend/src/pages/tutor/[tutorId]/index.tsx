import ProfileHeader from "@/components/profileHeader"
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
    <div className="relative w-full">
      <div className="h-full w-full p-12">
        <ProfileHeader name={data?.name} accountType="Tutor" />
      </div>
    </div>
  )
}
