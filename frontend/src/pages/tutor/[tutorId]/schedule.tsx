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
import useUser from "@/hooks/useUser"
import { cn, toastProtectedFnCall } from "@/lib/utils"
import { HTTPAppointmentService } from "@/service/appointmentService"
import { HTTPProfileService } from "@/service/profileService"
import { uniq } from "lodash"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useQuery, useQueryClient } from "react-query"

const profileService = new HTTPProfileService()
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
  const { data: scheduleData } = useQuery({
    queryKey: ["tutors", tutorId, "schedule"],
    queryFn: async () => {
      const { timesAvailable } = await profileService.getTutorProfile(tutorId)
      return timesAvailable.map((ta) => ({
        start: new Date(ta.startTime),
        end: new Date(ta.endTime),
      }))
    },
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
  })

  const { data: profileData } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: async () => {
      const tutorProfile = await profileService.getTutorProfile(tutorId)
      return tutorProfile
    },
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
  })

  const { data: tutorAppointmentData } = useQuery({
    queryKey: ["tutors", tutorId, "appointments"],
    queryFn: () => appointmentService.getTutorAppointments(tutorId),
  })

  const { data: studentAppointmentData } = useQuery({
    queryKey: ["student", user?.userId, "appointments"],
    queryFn: () => appointmentService.getOwnStudentAppointments(),
  })

  let tutorIds: string[] = []
  if (studentAppointmentData) {
    tutorIds = uniq([
      ...studentAppointmentData.requested.map((a) => a.tutorId),
      ...studentAppointmentData.completed.map((a) => a.tutorId),
      ...studentAppointmentData.accepted.map((a) => a.tutorId),
    ])
  }

  const { data: tutorNames } = useQuery({
    queryKey: ["tutors", tutorIds, "names"],
    queryFn: async () => {
      const profiles = await Promise.all(
        tutorIds.map((id) => profileService.getTutorProfile(id)),
      )
      const idMap = new Map<string, string>()
      profiles.forEach((profile) => idMap.set(profile.id, profile.name))
      return idMap
    },
  })

  if (!profileData || !tutorAppointmentData || !scheduleData || !tutorNames) {
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
          ...(tutorAppointmentData?.yourAppointments.map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            title: `${
              appointment.tutorAccepted ? "Appointment" : "Requested"
            } with ${profileData?.name}`,
            componentProps: {
              className: cn(
                "bg-green-300/40 border border-green-500",
                !appointment.tutorAccepted &&
                  "bg-slate-300/40 border-dashed border-slate-500",
              ),
              onClick: (e: React.SyntheticEvent) => {
                e.stopPropagation()
              },
            },
          })) || []),
          ...(studentAppointmentData?.requested
            .filter(
              (studentAppointment) =>
                !tutorAppointmentData.yourAppointments
                  .map((a) => a.id)
                  .includes(studentAppointment.id),
            )
            .map((appointment) => ({
              interval: {
                start: appointment.startTime,
                end: appointment.endTime,
              },
              title: `Requested with ${tutorNames?.get(appointment.tutorId)}`,
              componentProps: {
                className:
                  "bg-slate-50/40 border border-dashed border-slate-500",
                onClick: (e: React.SyntheticEvent) => e.stopPropagation(),
              },
            })) || []),
          ...(scheduleData?.map((interval) => ({
            interval,
            componentProps: {
              className: "bg-white -z-10 text-white/0",
            },
          })) || []),
        ]}
      />
      <Dialog
        open={creatingAppointment}
        onOpenChange={(open) => setCreatingAppointment(open)}
      >
        <DialogContent className="fade-in-0">
          <DialogHeader>
            Requesting appointment with {profileData?.name}
          </DialogHeader>
          <DialogDescription asChild>
            <EditAppointmentForm
              startTime={clickedStartTime}
              submitFn={async (start, end) => {
                await new Promise((resolve) => setTimeout(resolve, 1000))
                // toast(start.toString() + end.toString())
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
                  queryKey: ["tutors", tutorId, "appointments"],
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
