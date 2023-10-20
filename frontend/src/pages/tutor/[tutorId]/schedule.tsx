import SmartAvatar from "@/components/smartAvatar"
import WeeklyCalendar from "@/components/weeklyCalendar"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { addMinutes } from "date-fns"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useQuery } from "react-query"

const profileService = new HTTPProfileService()
export default function Schedule() {
  const { user } = useUser()
  const router = useRouter()
  const tutorId = router.query.tutorId as string
  const isOwnSchedule = user?.userId == tutorId
  const { data: scheduleData } = useQuery({
    queryKey: ["tutors", tutorId, "schedule"],
    queryFn: async () => {
      const { timesAvailable } = await profileService.getTutorProfile(tutorId)
      return timesAvailable.map((ta) => ({
        start: new Date(ta.startTime),
        end: new Date(ta.endTime),
      }))
    },
    onSuccess: (scheduleData) => setTestScheduleData(scheduleData),
  })
  const [testScheduleData, setTestScheduleData] = useState<
    {
      start: Date
      end: Date
    }[]
  >([])

  const { data: profileData } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: async () => {
      const tutorProfile = await profileService.getTutorProfile(tutorId)
      return tutorProfile
    },
  })
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
          setTestScheduleData([
            ...testScheduleData,
            { start: clickedDate, end: addMinutes(clickedDate, 60) },
          ])
        }}
        highlightedIntervals={testScheduleData}
      />
    </div>
  )
}
