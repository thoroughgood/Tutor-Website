import { NameFromTutorId } from "@/components/NameFromId"
import AppointmentDialog from "@/components/appointmentDialog"
import EditAppointmentForm from "@/components/editAppointmentForm"
import LoadingSpinner from "@/components/loadingSpinner"
import SmartAvatar from "@/components/smartAvatar"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
} from "@/components/ui/dialog"
import WeeklyCalendar from "@/components/weeklyCalendar"
import useStudentAppointments from "@/hooks/useStudentAppointments"
import useTutorAppointments from "@/hooks/useTutorAppointments"
import useUser from "@/hooks/useUser"
import useUserProfile from "@/hooks/useUserProfile"
import { toastProtectedFnCall } from "@/lib/utils"
import { HTTPAppointmentService } from "@/service/appointmentService"
import { TutorProfile } from "@/service/profileService"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useQueryClient } from "react-query"

const appointmentService = new HTTPAppointmentService()
export default function Schedule() {
  const queryClient = useQueryClient()
  const { user } = useUser()
  const router = useRouter()
  const tutorId = router.query.tutorId as string
  const isOwnSchedule = user?.userId == tutorId
  const [creatingAppointment, setCreatingAppointment] = useState(false)
  const [clickedStartTime, setClickedStartTime] = useState<undefined | Date>()

  if (isOwnSchedule) {
    router.push("/appointments")
  }
  const { profileData } = useUserProfile(tutorId) as {
    profileData: TutorProfile
  }
  const { requested, accepted, completed } = useStudentAppointments()
  const { other } = useTutorAppointments(tutorId)

  if (!profileData) {
    return <LoadingSpinner />
  }

  return (
    <div className="relative flex h-full w-full flex-col gap-10 overflow-hidden p-10">
      <div className="flex gap-4">
        <Link href={`/tutor/${tutorId}`}>
          <SmartAvatar
            className="h-16 w-16 text-3xl"
            loading={!profileData}
            name={profileData?.name}
            profilePicture={profileData?.profilePicture}
          />
        </Link>

        <h1 className="flex items-center text-xl ">
          <Link href={`/tutor/${tutorId}`} className="hover:underline">
            {profileData?.name}
          </Link>
          &apos;s&nbsp;Schedule
        </h1>
      </div>
      <WeeklyCalendar
        onCalendarClick={(clickedDate) => {
          setCreatingAppointment(true)
          setClickedStartTime(clickedDate)
        }}
        interactiveIntervals={[
          ...requested.map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            title: (
              <>
                Requested with <NameFromTutorId tutorId={appointment.tutorId} />
              </>
            ),
            componentProps: {
              children: <AppointmentDialog id={appointment.id} />,
              className:
                "bg-slate-100/40 border border-dashed border-slate-500",
              onClick: (e: React.SyntheticEvent) => e.stopPropagation(),
            },
          })),
          ...accepted.map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            title: (
              <>
                Appointment with{" "}
                <NameFromTutorId tutorId={appointment.tutorId} />
              </>
            ),
            componentProps: {
              children: <AppointmentDialog id={appointment.id} />,
              className: "bg-green-300/40 border border-green-400",
              onClick: (e: React.SyntheticEvent) => e.stopPropagation(),
            },
          })),
          ...completed.map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },

            title: (
              <>
                Completed appointment with{" "}
                <NameFromTutorId tutorId={appointment.tutorId} />
              </>
            ),
            componentProps: {
              children: <AppointmentDialog id={appointment.id} />,
              className: "bg-slate-200/40 border border-slate-400",
              onClick: (e: React.SyntheticEvent) => e.stopPropagation(),
            },
          })),
          ...profileData?.timesAvailable.map(({ startTime, endTime }) => ({
            interval: {
              start: new Date(startTime),
              end: new Date(endTime),
            },
            componentProps: {
              className: "bg-white -z-10 text-white/0",
            },
          })),
          ...other.map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            componentProps: {
              className: "bg-red-100 -z-10 text-white/0",
            },
          })),
        ]}
      />
      <Dialog
        open={creatingAppointment}
        onOpenChange={(open) => setCreatingAppointment(open)}
      >
        <DialogContent>
          <DialogHeader>
            Requesting appointment with {profileData?.name}
          </DialogHeader>
          <DialogDescription asChild>
            <EditAppointmentForm
              startTime={clickedStartTime}
              submitFn={async (start, end) => {
                await toastProtectedFnCall(
                  async () =>
                    await appointmentService.requestAppointment(
                      tutorId,
                      start,
                      end,
                    ),
                )
                setCreatingAppointment(false)
                queryClient.invalidateQueries({
                  queryKey: ["student", user?.userId, "appointments"],
                })
                return true
              }}
              cancelFn={() => setCreatingAppointment(false)}
            />
          </DialogDescription>
        </DialogContent>
      </Dialog>
    </div>
  )
}
