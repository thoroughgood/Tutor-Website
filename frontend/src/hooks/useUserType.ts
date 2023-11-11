import { HTTPProfileService } from "@/service/profileService"
import { useQuery } from "react-query"

const profileService = new HTTPProfileService()
export default function useUserType(userId?: string) {
  const { data } = useQuery({
    queryFn: () => profileService.getUserType(userId as string),
    queryKey: ["accountType", userId],
    enabled: !!userId,
  })
  return data
}
