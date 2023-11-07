import ToggleSwitch from "@/components/toggleSwitch"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { useState } from "react"

export default function Messages() {
  const [viewingAppointmentMessages, setViewingAppointmentMessages] =
    useState(true)
  return (
    <Card className="m-10">
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
      <CardContent>test</CardContent>
    </Card>
  )
}
