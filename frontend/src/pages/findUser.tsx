import IconInput from "@/components/iconInput"
import SmallProfileCard from "@/components/smallProfileCard"

import { cn } from "@/lib/utils"
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
  const [filterText, setFilterText] = useState("")
  const [filterOpen, setFilterOpen] = useState(false)

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

  const submitFilter = (e: React.SyntheticEvent) => {
    e.preventDefault()
    if (!courseOfferings?.includes(filterText) && filterText !== "") {
      setCourseOfferings([...(courseOfferings || []), filterText])
    }
    setFilterText("")
  }
  return (
    <div className="flex h-full w-full flex-col justify-center gap-10 p-16 md:justify-start">
      {/* Basic Inputs */}
      <div className="flex flex-col gap-2 rounded-md bg-secondary p-5 shadow-md">
        <h1 className="text-2xl text-secondary-foreground">
          Search For A User
        </h1>
        <div className="flex w-full flex-col gap-2 md:flex-row">
          <IconInput
            onChange={(e) => setName(e.currentTarget.value)}
            placeholder="Name"
          >
            <User className="h-5 w-5" />
          </IconInput>
          <IconInput
            onChange={(e) => setLocation(e.currentTarget.value)}
            placeholder="Location"
          >
            <MapPin className="h-5 w-5" />
          </IconInput>

          <input
            type="datetime-local"
            className={cn(
              "flex flex-row-reverse gap-2 rounded-md border px-4 py-2 text-muted-foreground",
              {
                "text-foreground": startTime !== null,
              },
            )}
            onChange={(e) => {
              const newTime =
                e.currentTarget.value === ""
                  ? null
                  : new Date(e.currentTarget.value)
              setStartTime(newTime)
              setEndTime(newTime)
            }}
          />
        </div>
      </div>
      {/* Tutor search results */}
      <div className="flex flex-wrap justify-center gap-5">
        {isLoading ? (
          <Loader2 className="animate-spin" />
        ) : (
          searchResp?.tutorIds.map((tId) => (
            <SmallProfileCard key={tId} id={tId} accountType="tutor" />
          ))
        )}
      </div>
    </div>
  )
}
