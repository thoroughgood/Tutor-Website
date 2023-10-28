import { format } from "date-fns"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogDescription,
} from "./ui/dialog"
import { useQuery } from "react-query"
import { HTTPAppointmentService } from "@/service/appointmentService"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { toastProtectedFnCall } from "@/lib/utils"
import LoadingButton from "./loadingButton"
import { useState } from "react"

interface AppointmentDialogProps {
  id: string
}
const appointmentService = new HTTPAppointmentService()
const profileService = new HTTPProfileService()
export default function AppointmentDialog({ id }: AppointmentDialogProps) {
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [acceptLoading, setAcceptLoading] = useState(false)
  const { data: appointmentData } = useQuery({
    queryKey: ["appointments", id],
    queryFn: async () => appointmentService.getAppointment(id),
    refetchOnWindowFocus: false,
    enabled: false,
  })
  const { data: tutorProfile } = useQuery({
    queryKey: ["tutors", appointmentData?.tutorId],
    queryFn: async () =>
      profileService.getTutorProfile(appointmentData?.tutorId as string),
    enabled: appointmentData !== undefined,
  })
  const { data: studentProfile } = useQuery({
    queryKey: ["students", appointmentData?.studentId],
    queryFn: async () =>
      profileService.getStudentProfile(appointmentData?.studentId as string),
    enabled: appointmentData !== undefined,
  })
  const { user } = useUser()
  if (!appointmentData) {
    return <div className="absolute left-0 top-0 h-full w-full" />
  }
  let userRole: "student" | "tutor" | "other" = "other"
  if (appointmentData.tutorId === user?.userId) {
    userRole = "tutor"
  } else if (appointmentData.studentId === user?.userId) {
    userRole = "student"
  }
  return (
    <Dialog>
      <DialogTrigger className="absolute left-0 top-0 h-full w-full " />
      <DialogContent>
        <DialogHeader>
          Requsted appointment with{" "}
          {userRole === "tutor" ? studentProfile?.name : tutorProfile?.name}
        </DialogHeader>
        <DialogDescription>
          {format(appointmentData.startTime, "MMM d | h:mmaaa")} –{" "}
          {format(appointmentData.endTime, "h:mmaaa")}
        </DialogDescription>
        {userRole === "tutor" && (
          <div className="flex justify-end gap-2">
            <LoadingButton
              isLoading={deleteLoading}
              variant="secondary"
              onClick={async () => {
                setDeleteLoading(true)
                await toastProtectedFnCall(() =>
                  appointmentService.deleteAppointment(id),
                )
                setDeleteLoading(false)
              }}
            >
              Decline
            </LoadingButton>
            <LoadingButton
              isLoading={acceptLoading}
              onClick={async () => {
                setAcceptLoading(true)
                await toastProtectedFnCall(() =>
                  appointmentService.acceptAppointment(id),
                )
                setAcceptLoading(false)
              }}
            >
              Accept
            </LoadingButton>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
