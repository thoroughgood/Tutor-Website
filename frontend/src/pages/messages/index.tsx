import MessageChannelPreview from "@/components/messageChannelPreview"
import ToggleSwitch from "@/components/toggleSwitch"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { HTTPMessageService } from "@/service/messageService"
import { useSearchParams } from "next/navigation"
import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { useQuery } from "react-query"

const messageService = new HTTPMessageService()
export default function Messages() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [viewingAppointmentMessages, setViewingAppointmentMessages] = useState(
    searchParams.get("viewing") === "appointment" || false,
  )
  const { data: directMessageChannels } = useQuery({
    queryKey: ["directMessages"],
    queryFn: async () => await messageService.getDirectChannelList(),
    enabled: !viewingAppointmentMessages,
  })
  const { data: appointmentChannels } = useQuery({
    queryKey: ["appointmentMessages"],
    queryFn: async () => await messageService.getAppointmentList(),
    enabled: viewingAppointmentMessages,
  })

  const channels = viewingAppointmentMessages
    ? appointmentChannels
    : directMessageChannels

  useEffect(() => {
    setViewingAppointmentMessages(
      searchParams.get("viewing") === "appointment" || false,
    )
  }, [router.pathname, searchParams])

  return (
    <div className="flex h-full w-full justify-center overflow-hidden">
      <Card className="m-0 flex max-w-3xl grow flex-col overflow-hidden pt-10  md:m-16 md:pt-0">
        <CardHeader>
          <ToggleSwitch
            toggledText="Appointment Messages"
            untoggledText="Direct Messages"
            isToggled={viewingAppointmentMessages}
            onClick={() => {
              setViewingAppointmentMessages(!viewingAppointmentMessages)
              router.push(
                router.pathname +
                  `?viewing=${
                    viewingAppointmentMessages ? "direct" : "appointment"
                  }`,
              )
            }}
            className="bg-muted"
          />
        </CardHeader>
        <CardContent className="flex flex-col gap-6 overflow-y-auto">
          {channels?.map((channelId) => (
            <MessageChannelPreview
              id={channelId}
              channelType={
                viewingAppointmentMessages ? "appointment" : "direct"
              }
              key={channelId}
            />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
