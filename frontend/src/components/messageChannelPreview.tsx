import {
  HTTPProfileService,
  StudentProfile,
  TutorProfile,
} from "@/service/profileService"
import { useQuery } from "react-query"
import SmartAvatar from "./smartAvatar"
import { prettySentence } from "@/lib/utils"
import Link from "next/link"

interface MessageChannelPreviewProps {
  id: string
  accountType: "tutor" | "student"
  channelType: "direct" | "appointment"
}

const profileService = new HTTPProfileService()
export default function MessageChannelPreview({
  id,
  accountType,
  channelType,
}: MessageChannelPreviewProps) {
  const { data: profileData } = useQuery<StudentProfile | TutorProfile>({
    queryKey: [`${accountType}s`, id],
    queryFn: async () =>
      accountType === "tutor"
        ? await profileService.getTutorProfile(id)
        : await profileService.getStudentProfile(id),
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
          {prettySentence(accountType)}
        </h5>
      </div>
    </Link>
  )
}
