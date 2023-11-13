import { HTTPProfileService } from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import { useState } from "react"
import useUser from "@/hooks/useUser"
import { Calendar, MessageSquare } from "lucide-react"
import { Skeleton } from "./ui/skeleton"
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
      <div className="mb-1 flex gap-2 border border-b-2 p-2 shadow">
        {data.type === "message" ? (
          <MessageSquare className="mt-1 text-muted-foreground" />
        ) : (
          <Calendar className="mt-2 text-muted-foreground" />
        )}
        <div className="mb-2 font-light"> {data.content}</div>
      </div>
    )
  } else {
    return <Skeleton className="h-12 w-full" />
  }
}
