import { useQuery } from "react-query"
import { HTTPProfileService } from "@/service/profileService"
import LoadingSpinner from "./loadingSpinner"

interface SmallProfileCard {
  id: string
  accountType: "tutor" | "student" // add more later if necessary
}

const profileService = new HTTPProfileService()

export default function Notification(notificationId: string) {
  const { data } = useQuery({
    queryKey: ["notifications", notificationId],
    queryFn: async () => {
      return await profileService.getNotification(notificationId)
    },
  })

  if (!data) {
    ;<LoadingSpinner />
  } else {
    return (
      <>
        <div>{data.content}</div>
      </>
    )
  }
}
