import Messages, { OptimisticMessage } from "@/components/messages"
import SmartAvatar from "@/components/smartAvatar"
import useUser from "@/hooks/useUser"
import useUserType from "@/hooks/useUserType"
import { HTTPAppointmentService } from "@/service/appointmentService"
import { HTTPMessageService, Message } from "@/service/messageService"
import { HTTPProfileService } from "@/service/profileService"
import { nanoid } from "nanoid"
import Link from "next/link"
import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "react-query"

const messageService = new HTTPMessageService()
const profileService = new HTTPProfileService()
const appointmentService = new HTTPAppointmentService()
export default function AppointmentMessage() {
  const router = useRouter()
  const appointmentId = router.query.appointmentId as string
  const { user } = useUser()
  const queryClient = useQueryClient()
  const { data: appointment } = useQuery({
    queryFn: async () => await appointmentService.getAppointment(appointmentId),
    queryKey: ["appointments", appointmentId],
  })
  const otherUserId =
    user?.userType === "student" ? appointment?.tutorId : appointment?.studentId
  const otherUserType = useUserType(otherUserId)

  const { data: otherUserProfile } = useQuery({
    queryKey: [`${otherUserType}s`, otherUserId],
    queryFn: async () => {
      if (otherUserType === "student") {
        return await profileService.getStudentProfile(otherUserId as string)
      }
      return await profileService.getTutorProfile(otherUserId as string)
    },
    enabled: !!otherUserType && !!otherUserId,
  })

  const { data: initialMessages } = useQuery({
    queryKey: ["messages", "appointment", appointmentId],
    queryFn: async () =>
      await messageService.getAppointmentMessages(otherUserId as string),
  })
  const { mutate: sendMessage } = useMutation({
    mutationFn: async (messageContent: string) =>
      await messageService.sendAppointmentMessage(
        appointmentId,
        messageContent,
      ),
    onMutate: async (messageContent: string) => {
      await queryClient.cancelQueries({
        queryKey: ["messages", "appointment", appointmentId],
      })
      const prevMessages = queryClient.getQueryData([
        "messages",
        "appointment",
        appointmentId,
      ])
      const optimisticMessage: OptimisticMessage = {
        isOptimistic: true,
        content: messageContent,
        id: "tmp-" + nanoid(),
      }
      queryClient.setQueryData<(Message | OptimisticMessage)[]>(
        ["messages", "appointment", appointmentId],
        (old) => [optimisticMessage, ...(old || [])],
      )
      return { prevMessages }
    },
    onSettled: () => {
      queryClient.invalidateQueries(["messages", "appointment", appointmentId])
    },
  })

  const [messages, setMessages] = useState<(Message | OptimisticMessage)[]>([])
  useEffect(() => {
    initialMessages && setMessages(initialMessages.toReversed())
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
              <h2 className="text-2xl">Appointment message with</h2>
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
