import { HTTPProfileService } from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import { useState } from "react"
import useUser from "@/hooks/useUser"
import LoadingSpinner from "./loadingSpinner"
import { Calendar, MessageSquare } from "lucide-react"
const profileService = new HTTPProfileService()

export interface NotificationInterface {
  notificationId: string
  isAccount: boolean
}

export default function Notification({
  notificationId,
  isAccount,
}: NotificationInterface) {
  //deleteOwnUserProfile needs to grab the id of the profile we are on
  const queryClient = useQueryClient()
  const [deleted, setDeleted] = useState<boolean>()
  const { user } = useUser()

  const { data } = useQuery({
    queryKey: ["notifications", notificationId],
    queryFn: async () => {
      return await profileService.getNotification(notificationId)
    },
  })
  if (data) {
    return (
      <div className="border-gray-20 mb-1 border-b-2 bg-gray-50">
        {data.type === "message" ? (
          <MessageSquare className="mt-1 text-muted-foreground" />
        ) : (
          <Calendar className="mt-2 text-muted-foreground" />
        )}
        <div className="mb-2 font-light"> {data.content}</div>
      </div>
    )
  } else {
    return <LoadingSpinner />
  }
}
