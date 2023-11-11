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

interface MessageChannelPreviewProps {
  id: string
  channelType: "direct" | "appointment"
}

const profileService = new HTTPProfileService()
export default function MessageChannelPreview({
  id,
  channelType,
}: MessageChannelPreviewProps) {
  const userType = useUserType(id)
  const { data: profileData } = useQuery<StudentProfile | TutorProfile>({
    queryKey: [`${userType}s`, id],
    queryFn: async () =>
      userType === "tutor"
        ? await profileService.getTutorProfile(id)
        : await profileService.getStudentProfile(id),
    enabled: !!userType,
  })

  return (
    <Link href={`/messages/${channelType}/${id}`} className="flex gap-4">
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
