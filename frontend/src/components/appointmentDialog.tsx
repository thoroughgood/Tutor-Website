import { format } from "date-fns"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogDescription,
} from "./ui/dialog"
import { useQuery, useQueryClient } from "react-query"
import { HTTPAppointmentService } from "@/service/appointmentService"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { prettySentence, toastProtectedFnCall } from "@/lib/utils"
import LoadingButton from "./loadingButton"
import { useState } from "react"
import EditAppointmentForm from "./editAppointmentForm"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu"
import { MoreVertical } from "lucide-react"
import Link from "next/link"
import Rating from "./rating"

interface AppointmentDialogProps {
  id: string
  status: "accepted" | "requested" | "completed"
}
const appointmentService = new HTTPAppointmentService()
const profileService = new HTTPProfileService()
export default function AppointmentDialog({
  id,
  status,
}: AppointmentDialogProps) {
  const queryClient = useQueryClient()
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [acceptLoading, setAcceptLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const { data: appointmentData } = useQuery({
    queryKey: ["appointments", id],
    queryFn: async () => appointmentService.getAppointment(id),
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
  let otherUserRole: "student" | "tutor" | "other" = "other"
  let otherUserId = ""
  if (appointmentData.tutorId === user?.userId) {
    userRole = "tutor"
    otherUserRole = "student"
    otherUserId = appointmentData.studentId || ""
  } else if (appointmentData.studentId === user?.userId) {
    userRole = "student"
    otherUserRole = "tutor"
    otherUserId = appointmentData.tutorId || ""
  }
  return (
    <Dialog onOpenChange={(open) => setOpen(open)} open={open}>
      <DialogTrigger className="absolute left-0 top-0 h-full w-full " />
      <DialogContent>
        <DialogHeader>
          {appointmentData.tutorAccepted
            ? "Appointment"
            : "Requested appointment"}{" "}
          with{" "}
          {userRole === "tutor" ? studentProfile?.name : tutorProfile?.name}
          <DropdownMenu>
            <DropdownMenuTrigger className="absolute right-10 top-2 p-2 text-muted-foreground transition hover:text-black">
              <MoreVertical width={15} height={15} />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>More Actions</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Link href={`${otherUserRole}/${otherUserId}`}>
                  View {prettySentence(otherUserRole)} Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Link href={`messages/appointment/${id}`}>
                  View Appointment Messages
                </Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </DialogHeader>
        <DialogDescription>
          <div className="flex flex-col gap-2">
            {format(appointmentData.startTime, "MMM d | h:mmaaa")} –{" "}
            {format(appointmentData.endTime, "h:mmaaa")}
            {userRole === "tutor" && appointmentData.tutorAccepted && (
              <EditAppointmentForm
                cancelFn={() => setOpen(false)}
                submitFn={async (start, end) => {
                  return await toastProtectedFnCall(async () => {
                    await appointmentService.modifyAppointment(id, start, end)
                    queryClient.invalidateQueries(["appointments", id])
                    setOpen(false)
                  })
                }}
                deleteFn={async () => {
                  return await toastProtectedFnCall(async () => {
                    await appointmentService.deleteAppointment(
                      appointmentData.id,
                    )
                    queryClient.invalidateQueries([
                      "tutors",
                      appointmentData.tutorId,
                      "appointments",
                    ])
                    setOpen(false)
                  })
                }}
                startTime={appointmentData.startTime}
                endTime={appointmentData.endTime}
              />
            )}
          </div>
          {userRole === "student" && status === "completed" && (
            <>
              <hr className="my-5" />
              <div className="flex justify-center">
                Rate your appointment with {tutorProfile?.name}
              </div>
              <div className="flex-column mt-1 justify-center">
                <Rating appointmentId={id} />
              </div>
            </>
          )}
        </DialogDescription>
        {userRole === "tutor" && !appointmentData.tutorAccepted && (
          <div className="flex justify-end gap-2">
            <LoadingButton
              isLoading={deleteLoading}
              variant="secondary"
              onClick={async () => {
                setDeleteLoading(true)
                await toastProtectedFnCall(() =>
                  appointmentService.deleteAppointment(id),
                )
                await queryClient.invalidateQueries([
                  "tutors",
                  user?.userId,
                  "appointments",
                ])
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
                await queryClient.invalidateQueries(["appointments", id])
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
