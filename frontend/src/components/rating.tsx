import { getErrorMessage } from "@/lib/utils"
import { HTTPAppointmentService } from "@/service/appointmentService"
import { HTTPProfileService } from "@/service/profileService"
import { Star } from "lucide-react"
import { useState } from "react"
import toast from "react-hot-toast"
import { useQuery } from "react-query"

const appointmentService = new HTTPAppointmentService()
const profileService = new HTTPProfileService()

interface ratingInterface {
  appointmentId: string
}

export default function Rating({ appointmentId }: ratingInterface) {
  const [rating, setRating] = useState(0)

  const { data } = useQuery({
    queryKey: ["ratings", rating],
    queryFn: () => appointmentService.getAppointment(appointmentId),
  })

  const handleStarClick = async (selectedRating: number) => {
    setRating(selectedRating)
    try {
      const resp = await profileService.rateTutor(appointmentId, selectedRating)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  if (data) {
    console.log(data)
  }

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
