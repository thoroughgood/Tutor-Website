import AppointmentDialog from "@/components/appointmentDialog"
import LoadingButton from "@/components/loadingButton"
import LoadingSpinner from "@/components/loadingSpinner"
import { Button } from "@/components/ui/button"
import WeeklyCalendar from "@/components/weeklyCalendar"
import useStudentAppointments from "@/hooks/useStudentAppointments"
import useUser from "@/hooks/useUser"
import {
  cn,
  excludeInterval,
  getErrorMessage,
  getMergedIntervals,
} from "@/lib/utils"
import {
  Appointment,
  HTTPAppointmentService,
} from "@/service/appointmentService"
import { HTTPProfileService } from "@/service/profileService"
import { areIntervalsOverlapping } from "date-fns"
import { omit } from "lodash"
import { useEffect, useState } from "react"
import toast from "react-hot-toast"
import { useQueries, useQuery, useQueryClient } from "react-query"

const profileService = new HTTPProfileService()
const appointmentService = new HTTPAppointmentService()
export default function Appointments() {
  const { user } = useUser()
  if (user?.userType === "tutor") {
    return <AppointmentsAsTutor />
  } else if (user?.userType === "student") {
    return <AppointmentsAsStudent />
  }
}

function AppointmentsAsStudent() {
  const { requested, completed, accepted } = useStudentAppointments()
  return (
    <div className="h-full w-full overflow-hidden p-6">
      <WeeklyCalendar
        className="bg-background"
        interactiveIntervals={[
          ...requested.map((appointment) => ({
            title: (
              <>
                Requested appointment with{" "}
                <NameFromTutorId tutorId={appointment.tutorId} />
              </>
            ),
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            componentProps: {
              children: (
                <AppointmentDialog id={appointment.id} status="requested" />
              ),
              className:
                "bg-slate-100/40 border border-dashed border-slate-500",
            },
          })),
          ...completed.map((appointment) => ({
            title: (
              <>
                Completed appointment with{" "}
                <NameFromTutorId tutorId={appointment.tutorId} />
              </>
            ),
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            componentProps: {
              children: (
                <AppointmentDialog id={appointment.id} status="completed" />
              ),
              className: "bg-slate-200/40 border border-slate-400",
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
              children: (
                <AppointmentDialog id={appointment.id} status="accepted" />
              ),
              className: "bg-green-300/40 border border-green-400",
            },
          })),
        ]}
      />
    </div>
  )
}

function AppointmentsAsTutor() {
  const { user } = useUser()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [intervals, setIntervals] = useState<Interval[]>([])
  const [mouseMode, setMouseMode] = useState<
    "available" | "unavailable" | "none"
  >("none")
  const [submitLoading, setSubmitLoading] = useState(false)

  const { data: initialIntervals } = useQuery({
    queryKey: ["tutors", user?.userId as string, "timeAvailable"],
    queryFn: async () => {
      const { timesAvailable } = await profileService.getTutorProfile(
        user?.userId as string,
      )
      return timesAvailable.map((ta) => ({
        start: new Date(ta.startTime),
        end: new Date(ta.endTime),
      }))
    },
  })
  const { data: tutorProfile } = useQuery({
    queryKey: ["tutors", user?.userId as string],
    queryFn: async () => profileService.getTutorProfile(user?.userId as string),
    enabled: user?.userId !== undefined,
  })

  const { data: tutorAppointments } = useQuery({
    queryKey: ["tutors", user?.userId, "appointments"],
    queryFn: async () =>
      appointmentService.getTutorAppointments(user?.userId as string),
    enabled: user?.userId !== undefined,
  })

  const appointmentIds = tutorAppointments?.yourAppointments
  const appointmentQueries = useQueries(
    appointmentIds?.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )

  useEffect(() => {
    setIntervals(initialIntervals || [])
  }, [initialIntervals])

  const setIntervalAvailable = (interval: Interval) => {
    setIntervals(getMergedIntervals([...intervals, interval]))
  }
  const setIntervalUnavailable = (interval: Interval) => {
    setIntervals(getMergedIntervals(excludeInterval(intervals, interval)))
  }

  if (!initialIntervals || !tutorProfile) {
    return <LoadingSpinner />
  }
  return (
    <div className="relative flex h-full w-full flex-col gap-2 overflow-hidden p-6 lg:p-16">
      <WeeklyCalendar
        onCalendarMouseMove={(interval) => {
          if (!isEditing || submitLoading) return
          if (mouseMode === "available") {
            setIntervalAvailable(interval)
          } else if (mouseMode === "unavailable") {
            setIntervalUnavailable(interval)
          }
        }}
        onCalendarMouseDown={(interval) => {
          if (!isEditing || submitLoading) return
          if (intervals.some((i) => areIntervalsOverlapping(i, interval))) {
            setMouseMode("unavailable")
            setIntervalUnavailable(interval)
          } else {
            setMouseMode("available")
            setIntervalAvailable(interval)
          }
        }}
        onCalendarMouseUp={() => setMouseMode("none")}
        onCalendarMouseLeave={() => setMouseMode("none")}
        interactiveIntervals={[
          ...intervals.map((interval) => ({
            interval: interval,
            componentProps: {
              className: "bg-white -z-10 text-white/0 select-none ",
            },
          })),
          ...(
            appointmentQueries
              .map((query) => query.data)
              .filter((data) => data !== undefined) as Appointment[]
          ).map((appointment) => ({
            interval: {
              start: appointment.startTime,
              end: appointment.endTime,
            },
            title: (
              <>
                {appointment.tutorAccepted
                  ? "Appointment with "
                  : "Appointment request from "}
                <NameFromStudentId studentId={appointment.studentId} />
              </>
            ),

            componentProps: {
              children: (
                <AppointmentDialog id={appointment.id} status="accepted" />
              ),
              className: cn(
                "bg-slate-100/40 border border-dashed border-slate-500",
                appointment.tutorAccepted &&
                  "bg-green-300/40 border-solid border-green-400",
              ),
            },
          })),
        ]}
      />
      <div className="flex justify-end gap-2">
        <Button
          variant={isEditing ? "secondary" : "default"}
          onClick={() => {
            if (isEditing) {
              setIntervals(initialIntervals)
            }
            setIsEditing(!isEditing)
          }}
        >
          {isEditing ? "Cancel Editing" : "Edit Schedule"}
        </Button>
        {isEditing && (
          <LoadingButton
            isLoading={submitLoading}
            onClick={async () => {
              setSubmitLoading(true)
              const newProfile = omit(tutorProfile, "id")
              newProfile.timesAvailable = intervals.map((i) => ({
                startTime: new Date(i.start).toISOString(),
                endTime: new Date(i.end).toISOString(),
              }))
              try {
                await profileService.setOwnTutorProfile(newProfile)
              } catch (error) {
                toast.error(getErrorMessage(error))
              }

              await queryClient.invalidateQueries([
                "tutors",
                user?.userId,
                "appointments",
              ])
              setSubmitLoading(false)
              setIsEditing(false)
            }}
          >
            Save Changes
          </LoadingButton>
        )}
      </div>
    </div>
  )
}

function NameFromStudentId({ studentId }: { studentId?: string }) {
  const { data: profileData } = useQuery({
    queryKey: ["students", studentId],
    queryFn: async () => profileService.getStudentProfile(studentId as string),
    enabled: studentId !== undefined,
  })
  return <>{profileData?.name}</>
}

function NameFromTutorId({ tutorId }: { tutorId?: string }) {
  const { data: profileData } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: async () => profileService.getTutorProfile(tutorId as string),
    enabled: tutorId !== undefined,
  })
  return <>{profileData?.name}</>
}
