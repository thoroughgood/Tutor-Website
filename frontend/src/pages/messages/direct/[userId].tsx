import Messages from "@/components/messages"
import SmartAvatar from "@/components/smartAvatar"
import useUser from "@/hooks/useUser"
import { HTTPMessageService, Message } from "@/service/messageService"
import { HTTPProfileService } from "@/service/profileService"
import Link from "next/link"
import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { useMutation, useQuery } from "react-query"

const messageService = new HTTPMessageService()
const profileService = new HTTPProfileService()
export default function DirectMessage() {
  const router = useRouter()
  const otherUserId = router.query.userId as string
  const { user } = useUser()

  const { data: otherUserProfile } = useQuery({
    queryKey: [user?.userType === "tutor" ? "students" : "tutors", otherUserId],
    queryFn: async () => {
      if (user?.userType === "tutor") {
        return await profileService.getStudentProfile(otherUserId)
      }
      return await profileService.getTutorProfile(otherUserId)
    },
  })

  const { data: initialMessages } = useQuery({
    queryKey: ["messages", "direct", user?.userId],
    queryFn: async () => await messageService.getDirectMessages(otherUserId),
  })
  const { mutate: sendMessage } = useMutation({
    mutationFn: async (messageContent: string) =>
      await messageService.sendDirectMessage(otherUserId, messageContent),
    mutationKey: ["messages", "direct", user?.userId],
    onSuccess: (newMessageResp, content) => {
      const newMessageObj: Message = {
        ...newMessageResp,
        sentBy: user?.userId || "",
        content,
      }
      setMessages([...messages, newMessageObj])
    },
  })

  const [messages, setMessages] = useState<Message[]>([])
  useEffect(() => {
    initialMessages && setMessages(initialMessages)
  }, [initialMessages])
  return (
    <div className="flex h-full w-full flex-col p-8">
      <Messages
        header={
          <Link
            href={`/${
              user?.userType === "tutor" ? "student" : "tutor"
            }/${otherUserId}`}
            className="flex gap-4"
          >
            <SmartAvatar
              profilePicture={otherUserProfile?.profilePicture}
              name={otherUserProfile?.name}
              className="h-20 w-20"
            />
            <div className="flex flex-col justify-center">
              <h2 className="text-2xl">Direct message with</h2>
              <h3>{otherUserProfile?.name}</h3>
            </div>
          </Link>
        }
        className="mx-auto h-full w-full max-w-2xl"
        messages={messages}
        sendMessage={sendMessage}
      />
    </div>
  )
}
