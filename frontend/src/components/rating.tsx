import { getErrorMessage } from "@/lib/utils"
import { HTTPProfileService } from "@/service/profileService"
import { Star } from "lucide-react"
import { useState } from "react"
import toast from "react-hot-toast"

const profileService = new HTTPProfileService()

interface ratingInterface {
  appointmentId: string
}

export default function Rating({ appointmentId }: ratingInterface) {
  const [rating, setRating] = useState(0)

  const handleStarClick = async (selectedRating: number) => {
    setRating(selectedRating)
    try {
      const resp = await profileService.rateTutor(appointmentId, selectedRating)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
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
