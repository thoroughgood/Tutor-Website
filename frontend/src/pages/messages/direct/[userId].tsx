import Messages, { OptimisticMessage } from "@/components/messages"
import SmartAvatar from "@/components/smartAvatar"
import { Button } from "@/components/ui/button"
import useUser from "@/hooks/useUser"
import useUserType from "@/hooks/useUserType"
import { HTTPMessageService, Message } from "@/service/messageService"
import { HTTPProfileService } from "@/service/profileService"
import { nanoid } from "nanoid"
import Link from "next/link"
import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "react-query"
import Pusher from "pusher-js"

const messageService = new HTTPMessageService()
const profileService = new HTTPProfileService()
export default function DirectMessage() {
  const router = useRouter()
  const otherUserId = router.query.userId as string
  const otherUserType = useUserType(otherUserId)
  const { user } = useUser()
  const queryClient = useQueryClient()
  useEffect(() => {
    const pusherClient = new Pusher(
      process.env.NEXT_PUBLIC_PUSHER_KEY as string,
      {
        cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER as string,
      },
    )
    const channel = pusherClient.subscribe(user?.userId as string)
    channel.bind("direct_message", () => {
      queryClient.invalidateQueries(["messages", "direct", user?.userId])
    })

    return () => channel.unsubscribe()
  }, [queryClient, user?.userId])

  const { data: otherUserProfile } = useQuery({
    queryKey: [`${otherUserType}s`, otherUserId],
    queryFn: async () => {
      if (otherUserType === "student") {
        return await profileService.getStudentProfile(otherUserId)
      }
      return await profileService.getTutorProfile(otherUserId)
    },
    enabled: !!otherUserType,
  })

  const { data: initialMessages } = useQuery({
    queryKey: ["messages", "direct", user?.userId],
    queryFn: async () => await messageService.getDirectMessages(otherUserId),
  })
  const { mutate: sendMessage } = useMutation({
    mutationFn: async (messageContent: string) =>
      await messageService.sendDirectMessage(otherUserId, messageContent),
    onMutate: async (messageContent: string) => {
      await queryClient.cancelQueries({
        queryKey: ["messages", "direct", user?.userId],
      })
      const prevMessages = queryClient.getQueryData([
        "messages",
        "direct",
        user?.userId,
      ])
      const optimisticMessage: OptimisticMessage = {
        isOptimistic: true,
        content: messageContent,
        id: "tmp-" + nanoid(),
      }
      queryClient.setQueryData<(Message | OptimisticMessage)[]>(
        ["messages", "direct", user?.userId],
        (old) => [optimisticMessage, ...(old || [])],
      )
      return { prevMessages }
    },
    onSettled: () => {
      queryClient.invalidateQueries(["messages", "direct", user?.userId])
    },
  })

  const [messages, setMessages] = useState<(Message | OptimisticMessage)[]>([])
  useEffect(() => {
    initialMessages && setMessages(initialMessages.toReversed())
  }, [initialMessages])
  return (
    <div className="flex h-full w-full flex-col gap-4 p-8">
      <Button
        variant="secondary"
        className="w-fit justify-self-start"
        onClick={() => router.back()}
      >
        Back
      </Button>
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
