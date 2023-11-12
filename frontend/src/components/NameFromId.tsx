import { HTTPProfileService } from "@/service/profileService"
import { useQuery } from "react-query"

const profileService = new HTTPProfileService()
export function NameFromStudentId({ studentId }: { studentId?: string }) {
  const { data: profileData } = useQuery({
    queryKey: ["students", studentId],
    queryFn: async () => profileService.getStudentProfile(studentId as string),
    enabled: studentId !== undefined,
  })
  return <>{profileData?.name}</>
}

export function NameFromTutorId({ tutorId }: { tutorId?: string }) {
  const { data: profileData } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: async () => profileService.getTutorProfile(tutorId as string),
    enabled: tutorId !== undefined,
  })
  return <>{profileData?.name}</>
}
