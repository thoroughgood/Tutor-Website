import { useState } from "react"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import { useQuery, useQueryClient } from "react-query"
import Notification from "./notification"
import LoadingSpinner from "./loadingSpinner"
const profileService = new HTTPProfileService()

export interface notificationsInterface {
  Notifications: string[]
}

export default function NotificationBox() {
  //here we are going to generate documentImg depending on the number of ids we have
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const userId = router.query.tutorId as string
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()
  const isAccount = userId === user?.userId

  const { data } = useQuery({
    queryKey: ["notifications", user?.userId],
    queryFn: async () => {
      return await profileService.getNotifications()
    },
  })
  console.log(data)
  if (!data) {
    return <LoadingSpinner />
  } else if (data.notifications.length === 0) {
    return (
      <div className="-mt-4 flex justify-center text-red-500">
        No notifications right now
      </div>
    )
  } else {
    return (
      <div className="-mt-2">
        <div className="flex justify-center">Notifications</div>
        <hr />

        <div className="flex flex-col items-center p-1">
          {data.notifications.map((tId) => (
            <Notification
              key={tId}
              notificationId={tId}
              isAccount={isAccount}
            />
          ))}
        </div>
      </div>
    )
  }
}
