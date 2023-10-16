import IconInput from "@/components/iconInput"
import SmallProfileCard from "@/components/smallProfileCard"
import { HTTPProfileService } from "@/service/profileService"
import { Loader2, MapPin, User } from "lucide-react"
import { useMemo, useState } from "react"
import { useQuery } from "react-query"
import { useDebounce } from "usehooks-ts"

const profileService = new HTTPProfileService()
export default function FindTutor() {
  const [name, setName] = useState<string>("")
  const [location, setLocation] = useState<string>("")
  const [rating, setRating] = useState<null | number>(null)
  const [courseOfferings, setCourseOfferings] = useState<null | string[]>(null)
  const [startTime, setStartTime] = useState<null | Date>(null)
  const [endTime, setEndTime] = useState<null | Date>(null)

  const searchParams = useMemo(() => {
    // Build the param obj from all the fields
    // Deletes key if 'null' since we want to use whitelist filtering
    const allParams = {
      name: name === "" ? null : name,
      location: location === "" ? null : location,
      rating,
      courseOfferings,
      timeRange: {
        startTime,
        endTime,
      },
    }
    return Object.fromEntries(
      Object.entries(allParams).filter(
        ([k, v]) =>
          v !== null &&
          !(k === "timeRange" && (startTime === null || endTime === null)),
      ),
    )
  }, [name, location, rating, courseOfferings, startTime, endTime])

  const debouncedSearchParams = useDebounce(searchParams, 250)

  const { data: searchResp, isLoading } = useQuery({
    queryKey: ["tutors", debouncedSearchParams],
    queryFn: async () => {
      return await profileService.searchTutors(debouncedSearchParams)
    },
  })
  return (
    <div className="h-full w-full p-16">
      <div className="flex w-full gap-2">
        <IconInput
          onChange={(e) => setName(e.currentTarget.value)}
          placeholder="Name"
        >
          <User />
        </IconInput>
        <IconInput
          onChange={(e) => setLocation(e.currentTarget.value)}
          placeholder="Location"
        >
          <MapPin />
        </IconInput>
      </div>
      {isLoading ? (
        <Loader2 className="animate-spin" />
      ) : (
        searchResp?.tutorIds.map((tId) => (
          <SmallProfileCard key={tId} id={tId} accountType="tutor" />
        ))
      )}
    </div>
  )
}
