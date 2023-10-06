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

  if (!data) {
    return <div>loading</div>
  }

  return (
    <div className="relative w-full">
      <div className="h-full w-full p-12">
        <ProfileHeader
          className="mx-auto max-w-xl"
          name={data.name}
          accountType="Tutor"
          email={data.email}
          profilePicture={data.profilePicture}
          phoneNumber={data.phoneNumber}
          location={data.location}
        />
      </div>
    </div>
  )
}
