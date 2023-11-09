import DocumentModal from "@/components/documentModal"
import HeaderSeparator from "@/components/headerSeparator"
import LoadingSpinner from "@/components/loadingSpinner"
import ProfileHeader from "@/components/profileHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"

import { Calendar, MessageCircle, User } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/router"
import { useState } from "react"
import { useQuery } from "react-query"

const profileService = new HTTPProfileService()
export default function TutorProfile() {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const { user } = useUser()
  const tutorId = router.query.tutorId as string
  const isOwnProfile = tutorId === user?.userId
  const { data } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: () => profileService.getTutorProfile(tutorId),
  })

  if (!data) {
    return <LoadingSpinner />
  }
  const docIds = data.documentIds

  //need to loop over document ids and get them from the backend, then display images of them

  console.log(data.documentIds)

  return (
    <div className="h-full w-full p-12">
      <div className="mx-auto flex max-w-xl flex-col gap-3">
        <ProfileHeader
          className="mx-auto max-w-xl"
          name={data.name}
          accountType="Tutor"
          email={data.email}
          profilePicture={data.profilePicture}
          phoneNumber={data.phoneNumber}
          location={data.location}
        />
        <div className="grid grid-cols-2 gap-2">
          {isOwnProfile ? (
            <>
              <Button asChild variant="secondary" className="flex gap-2">
                <Link className="" href={`${user?.userId}/edit`}>
                  <User className="w-5" />
                  Edit Profile
                </Link>
              </Button>

              <Button variant="default" className="flex gap-2">
                <Calendar className="w-5" />
                Edit Schedule
              </Button>
            </>
          ) : (
            <>
              <Button variant="secondary" className="flex gap-2">
                <MessageCircle className="w-5" />
                Message Tutor
              </Button>
              <Button asChild variant="default" className="flex gap-2">
                <Link href={`/tutor/${tutorId}/schedule`}>
                  <Calendar className="w-5" />
                  Create Appointment
                </Link>
              </Button>
            </>
          )}
        </div>
        <HeaderSeparator>Course Offerings</HeaderSeparator>
        <div className="flex gap-2">
          {data.courseOfferings.map((offering) => (
            <Badge key={offering} variant="random">
              {offering}
            </Badge>
          ))}
        </div>
        <Card className="mt-5">
          <CardHeader>
            <CardTitle>About me</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap">{data.bio}</div>
          </CardContent>
        </Card>
        <DocumentModal documentIds={data.documentIds} />
      </div>
    </div>
  )
}
