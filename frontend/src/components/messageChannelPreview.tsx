import {
  HTTPProfileService,
  StudentProfile,
  TutorProfile,
} from "@/service/profileService"
import { useQuery } from "react-query"
import SmartAvatar from "./smartAvatar"
import { prettySentence } from "@/lib/utils"
import Link from "next/link"
import useUserType from "@/hooks/useUserType"
import useUser from "@/hooks/useUser"
import useAppointmentQuery from "@/hooks/useAppointmentQuery"
import useUserProfile from "@/hooks/useUserProfile"
import { format } from "date-fns"

interface MessageChannelPreviewProps {
  id: string
  channelType: "direct" | "appointment"
}

const profileService = new HTTPProfileService()
export default function MessageChannelPreview({
  id,
  channelType,
}: MessageChannelPreviewProps) {
  if (channelType === "direct") {
    return <DirectChannelPreview userId={id} />
  }
  return <AppointmentChannelPreview appointmentId={id} />
}

function AppointmentChannelPreview({
  appointmentId,
}: {
  appointmentId: string
}) {
  const { user } = useUser()
  const { data: appointment } = useAppointmentQuery(appointmentId)
  const { profileData: tutorProfile } = useUserProfile(appointment?.tutorId)
  const { profileData: studentProfile } = useUserProfile(appointment?.studentId)
  const otherProfile =
    user?.userId === appointment?.tutorId ? studentProfile : tutorProfile
  return (
    <Link
      href={`/messages/appointment/${appointmentId}`}
      className="flex gap-4"
    >
      <SmartAvatar
        className="h-20 w-20"
        profilePicture={otherProfile?.profilePicture}
        name={otherProfile?.name}
        loading={!otherProfile}
      />
      <div className="flex flex-col justify-center">
        <h4>{otherProfile?.name}</h4>
        <h5 className="text-sm text-muted-foreground">
          {appointment?.startTime && appointment.endTime && (
            <>
              {format(appointment?.startTime, "MMM do p")} to{" "}
              {format(appointment?.endTime, "p")}
            </>
          )}
        </h5>
      </div>
    </Link>
  )
}

function DirectChannelPreview({ userId }: { userId: string }) {
  const userType = useUserType(userId)
  const { data: profileData } = useQuery<StudentProfile | TutorProfile>({
    queryKey: [`${userType}s`, userId],
    queryFn: async () =>
      userType === "tutor"
        ? await profileService.getTutorProfile(userId)
        : await profileService.getStudentProfile(userId),
    enabled: !!userType,
  })
  return (
    <Link href={`/messages/direct/${userId}`} className="flex gap-4">
      <SmartAvatar
        className="h-20 w-20"
        profilePicture={profileData?.profilePicture}
        name={profileData?.name}
        loading={!profileData}
      />
      <div className="flex flex-col justify-center">
        <h4>{profileData?.name}</h4>
        <h5 className="text-sm text-muted-foreground">
          {prettySentence(userType || "")}
        </h5>
      </div>
    </Link>
  )
}
