import MessageChannelPreview from "@/components/messageChannelPreview"
import ToggleSwitch from "@/components/toggleSwitch"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { HTTPMessageService } from "@/service/messageService"
import { useState } from "react"
import { useQuery } from "react-query"

const messageService = new HTTPMessageService()
export default function Messages() {
  const [viewingAppointmentMessages, setViewingAppointmentMessages] =
    useState(false)
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

  return (
    <div className="flex h-full w-full justify-center overflow-hidden">
      <Card className="m-0 flex max-w-3xl grow flex-col overflow-hidden pt-10  md:m-16 md:pt-0">
        <CardHeader>
          <ToggleSwitch
            toggledText="Appointment Messages"
            untoggledText="Direct Messages"
            isToggled={viewingAppointmentMessages}
            onClick={() =>
              setViewingAppointmentMessages(!viewingAppointmentMessages)
            }
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
