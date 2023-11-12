import IconInput from "@/components/iconInput"
import SmallProfileCard from "@/components/smallProfileCard"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { HTTPProfileService } from "@/service/profileService"
import { addMinutes, format } from "date-fns"
import { Loader2, MapPin, Star, User } from "lucide-react"
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
      rating: rating,
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
    <div className="flex h-full w-full flex-col justify-center gap-10 p-10 md:justify-start">
      {/* Basic Inputs */}
      <div className="flex flex-col gap-2 rounded-md border p-5 shadow-md">
        <h1 className="text-2xl text-secondary-foreground">
          Search For A Tutor
        </h1>
        <div className="flex w-full flex-col gap-2 md:flex-row">
          <IconInput
            value={name}
            onChange={(e) => setName(e.currentTarget.value)}
            placeholder="Name"
          >
            <User className="h-5 w-5" />
          </IconInput>
          <IconInput
            value={location}
            onChange={(e) => setLocation(e.currentTarget.value)}
            placeholder="Location"
          >
            <MapPin className="h-5 w-5" />
          </IconInput>
          <IconInput
            type="number"
            min={1}
            max={5}
            onChange={(e) => {
              if (e.currentTarget.value === "") {
                setRating(null)
              } else {
                const min = 1
                const max = 5
                const clamp = (num: number, min: number, max: number) =>
                  Math.min(Math.max(num, 0), max)
                const rating = clamp(Number(e.currentTarget.value), min, max)
                setRating(rating)
              }
            }}
            placeholder="Rating"
          >
            <Star className="h-5 w-5" />
          </IconInput>

          <input
            type="datetime-local"
            className={cn(
              "flex flex-row-reverse gap-2 rounded-md border px-4 py-2 text-muted-foreground",
              {
                "text-foreground": startTime !== null,
              },
            )}
            value={
              startTime !== null ? format(startTime, "yyyy-MM-dd hh:mm") : ""
            }
            onChange={(e) => {
              const newTime =
                e.currentTarget.value === ""
                  ? null
                  : new Date(e.currentTarget.value)
              setStartTime(newTime)
              setEndTime(newTime)
              newTime && setEndTime(addMinutes(newTime, 15))
            }}
          />
        </div>

        {/* Filters */}
        <div className="flex flex-row flex-wrap justify-center gap-2 md:justify-start">
          <Popover
            open={filterOpen}
            onOpenChange={(open) => setFilterOpen(open)}
          >
            <PopoverTrigger asChild>
              <Button size="sm" onClick={() => setFilterOpen(true)}>
                + Add Course Filter
              </Button>
            </PopoverTrigger>
            <PopoverContent>
              <form onClick={submitFilter} className="flex flex-col gap-2">
                <Label>Add Course Filter</Label>
                <Input
                  onChange={(e) => setFilterText(e.currentTarget.value)}
                  value={filterText}
                />
                <div className="grid grid-cols-2 gap-4">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setFilterOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button size="sm">Submit</Button>
                </div>
              </form>
            </PopoverContent>
          </Popover>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setCourseOfferings(null)}
          >
            × Clear Courses
          </Button>
        </div>

        {courseOfferings && (
          <div className="flex flex-wrap justify-center gap-2 md:justify-start">
            {courseOfferings?.map((course) => (
              <Badge
                className="inline-flex w-fit"
                key={course}
                variant="random"
              >
                {course}
              </Badge>
            ))}
          </div>
        )}
        <Button
          className="w-fit"
          variant="secondary"
          size="sm"
          onClick={() => {
            setName("")
            setLocation("")
            setStartTime(null)
            setEndTime(null)
            setCourseOfferings(null)
          }}
        >
          × Clear All Filters
        </Button>
      </div>

      {/* Tutor search results */}
      <div className="flex flex-wrap justify-center gap-5 overflow-y-auto p-2">
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
