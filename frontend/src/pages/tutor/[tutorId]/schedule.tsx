import EditAppointmentForm from "@/components/editAppointmentForm"
import SmartAvatar from "@/components/smartAvatar"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
} from "@/components/ui/dialog"
import WeeklyCalendar from "@/components/weeklyCalendar"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { zodResolver } from "@hookform/resolvers/zod"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useForm } from "react-hook-form"
import toast from "react-hot-toast"
import { useQuery } from "react-query"
import { z } from "zod"

const formSchema = z.object({
  day: z.string(),
  startTime: z.string(),
  endTime: z.string(),
})

const profileService = new HTTPProfileService()
export default function Schedule() {
  const { user } = useUser()
  const router = useRouter()
  const tutorId = router.query.tutorId as string
  const isOwnSchedule = user?.userId == tutorId
  const [creatingAppointment, setCreatingAppointment] = useState(false)
  const [clickedStartTime, setClickedStartTime] = useState<undefined | Date>()

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

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  const onSubmit = (values: z.infer<typeof formSchema>) => {
    console.log(values)
  }
  console.log("what")
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
        highlightedIntervals={scheduleData || []}
      />
      <Dialog
        open={creatingAppointment}
        onOpenChange={(open) => setCreatingAppointment(open)}
      >
        <DialogContent className="fade-in-0">
          <DialogHeader>
            Requesting appointment with {profileData?.name}
          </DialogHeader>
          <DialogDescription>
            <EditAppointmentForm
              startTime={clickedStartTime}
              submitFn={async (start, end) => {
                await new Promise((resolve) => setTimeout(resolve, 1000))
                toast(start.toString() + end.toString())
                return true
              }}
              cancelFn={() => {}}
            />
          </DialogDescription>
        </DialogContent>
      </Dialog>
    </div>
  )
}
