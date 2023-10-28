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
import useUser from "@/hooks/useUser"
import { toastProtectedFnCall } from "@/lib/utils"
import {
  Appointment,
  HTTPAppointmentService,
} from "@/service/appointmentService"
import { HTTPProfileService } from "@/service/profileService"
import { uniq } from "lodash"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useQueries, useQuery, useQueryClient } from "react-query"

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
  })

  const { data: studentAppointmentIds } = useQuery({
    queryKey: ["student", user?.userId, "appointments"],
    queryFn: () => appointmentService.getOwnStudentAppointments(),
  })

  const reqAppointmentsQueries = useQueries(
    studentAppointmentIds?.requested.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )
  const acceptedAppointmentQueries = useQueries(
    studentAppointmentIds?.accepted.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )
  const completedAppointmentQueries = useQueries(
    studentAppointmentIds?.completed.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )

  const tutorIds = uniq(
    (
      [
        ...reqAppointmentsQueries,
        ...acceptedAppointmentQueries,
        ...completedAppointmentQueries,
      ]
        .map((query) => query.data)
        .filter((data) => data !== undefined) as Appointment[]
    ).map((appointment) => appointment.tutorId),
  )

  const userProfilesQueries = useQueries(
    tutorIds.map((id) => ({
      queryKey: ["tutors", id],
      queryFn: async () => profileService.getTutorProfile(id),
    })),
  )

  const userNameMap = new Map<string, string>()
  userProfilesQueries.forEach(
    (query) => query.data && userNameMap.set(query.data.id, query.data.name),
  )

  if (!profileData || !scheduleData) {
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
          ...((
            reqAppointmentsQueries
              .map((query) => query.data)
              .filter((data) => data !== undefined) as Appointment[]
          ).map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            title: `Requested with ${userNameMap.get(appointment.tutorId)}`,
            componentProps: {
              children: <AppointmentDialog id={appointment.id} />,
              className:
                "bg-slate-100/40 border border-dashed border-slate-500",
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
