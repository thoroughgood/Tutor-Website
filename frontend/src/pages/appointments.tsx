import LoadingButton from "@/components/loadingButton"
import LoadingSpinner from "@/components/loadingSpinner"
import { Button } from "@/components/ui/button"
import WeeklyCalendar from "@/components/weeklyCalendar"
import useUser from "@/hooks/useUser"
import {
  excludeInterval,
  getErrorMessage,
  getMergedIntervals,
} from "@/lib/utils"
import { HTTPProfileService } from "@/service/profileService"
import { areIntervalsOverlapping } from "date-fns"
import { omit } from "lodash"
import { useEffect, useState } from "react"
import toast from "react-hot-toast"
import { useQuery, useQueryClient } from "react-query"

const profileService = new HTTPProfileService()
export default function Appointments() {
  const { user } = useUser()
  if (user?.userType === "tutor") {
    return <AppointmentsAsTutor />
  } else if (user?.userType === "student") {
    return <AppointmentsAsStudent />
  }
}

function AppointmentsAsStudent() {
  return <div>studnetappointment</div>
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
  })

  useEffect(() => {
    setIntervals(initialIntervals || [])
  }, [initialIntervals])

  const setIntervalAvialable = (interval: Interval) => {
    setIntervals(getMergedIntervals([...intervals, interval]))
  }
  const setIntervalUnavailable = (interval: Interval) => {
    setIntervals(getMergedIntervals(excludeInterval(intervals, interval)))
  }

  if (!initialIntervals || !tutorProfile) {
    return <LoadingSpinner />
  }
  return (
    <div className="relative flex h-full w-full flex-col gap-2 overflow-hidden p-16">
      <WeeklyCalendar
        onCalendarMouseMove={(interval) => {
          if (!isEditing || submitLoading) return
          if (mouseMode === "available") {
            setIntervalAvialable(interval)
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
            setIntervalAvialable(interval)
          }
        }}
        onCalendarMouseUp={() => setMouseMode("none")}
        onCalendarMouseLeave={() => setMouseMode("none")}
        interactiveIntervals={intervals.map((interval) => ({
          interval: interval,
          componentProps: {
            className: "bg-white -z-10 text-white/0 select-none ",
          },
        }))}
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

              await queryClient.invalidateQueries("tutors")
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
