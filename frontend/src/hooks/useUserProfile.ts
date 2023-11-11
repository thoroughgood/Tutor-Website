import {
  HTTPProfileService,
  StudentProfile,
  TutorProfile,
} from "@/service/profileService"
import useUserType from "./useUserType"
import { useQuery } from "react-query"

const profileService = new HTTPProfileService()
export default function useUserProfile(userId?: string) {
  const userType = useUserType(userId)
  const { data: profileData } = useQuery<StudentProfile | TutorProfile>({
    queryKey: [`${userType}s`, userId],
    queryFn: async () =>
      userType === "tutor"
        ? await profileService.getTutorProfile(userId as string)
        : await profileService.getStudentProfile(userId as string),
    enabled: !!userType,
  })
  return { profileData, userType }
}
