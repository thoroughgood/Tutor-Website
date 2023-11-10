import { getErrorMessage } from "@/lib/utils"
import { HTTPAppointmentService } from "@/service/appointmentService"
import { HTTPProfileService } from "@/service/profileService"
import { Star } from "lucide-react"
import { useEffect, useState } from "react"
import toast from "react-hot-toast"
import { useQuery, useQueryClient } from "react-query"
import LoadingSpinner from "./loadingSpinner"

const appointmentService = new HTTPAppointmentService()
const profileService = new HTTPProfileService()

interface ratingInterface {
  appointmentId: string
}

export default function Rating({ appointmentId }: ratingInterface) {
  const [rating, setRating] = useState<number>(0)
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: ["ratings", appointmentId],
    queryFn: () => appointmentService.getAppointment(appointmentId),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
    staleTime: 1000 * 60 * 5,
    // Set enabled to false to prevent automatic fetching
  })

  const handleStarClick = async (selectedRating: number) => {
    setRating(selectedRating)
    try {
      const resp = await profileService.rateTutor(appointmentId, selectedRating)
      queryClient.invalidateQueries(["ratings", appointmentId])
      console.log(resp)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  //useEffect will call data only when data is modified.
  //will be modified only on first call
  useEffect(() => {
    if (data) {
      console.log("this is data.rating" + data.rating)
      setRating(data.rating as number)
    }
  }, [data])

  if (!data) {
    return <LoadingSpinner />
  } else {
    return (
      <>
        <div className="flex gap-1 pb-3 pl-[35%]">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              onClick={() => handleStarClick(star)}
              style={{
                cursor: "pointer",
                fill: star <= rating ? "gold" : "gray",
                color: star <= rating ? "gold" : "gray",
              }}
            />
          ))}
        </div>
      </>
    )
  }
}
