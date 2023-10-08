import { cn } from "@/lib/utils"
import { useEffect, useRef, useState } from "react"
import {
  setDay,
  setWeek,
  format,
  getWeek,
  isSameDay,
  setHours,
  areIntervalsOverlapping,
} from "date-fns"
import { Button } from "./ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface WeeklyCalendarProps {
  className?: string
  highlightedIntervals: Interval[]
}
export default function WeeklyCalendar({
  className,
  highlightedIntervals,
}: WeeklyCalendarProps) {
  const [calHeight, setCalHeight] = useState(0)
  const [calWidth, setCalWidth] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const topRef = useRef<HTMLDivElement>(null)
  const sideRef = useRef<HTMLDivElement>(null)

  const [viewWeek, setViewWeek] = useState(getWeek(new Date()))
  const [weekDate, setWeekDate] = useState(new Date())

  useEffect(() => {
    setWeekDate(setWeek(new Date(), viewWeek))
  }, [viewWeek])

  useEffect(() => {
    const onResize = () => {
      setCalWidth(scrollRef.current?.scrollWidth || 0)
    }

    window.onresize = onResize
    if (scrollRef.current) {
      const height = scrollRef.current.scrollHeight
      setCalHeight(height)
      setCalWidth(scrollRef.current.scrollWidth)
      scrollRef.current.scrollTo(0, (height / 24) * 7 + 10)
    }
    return () => window.removeEventListener("resize", onResize)
  }, [])

  return (
    <div className="flex h-full w-full flex-col gap-3">
      <div className="ml-[50px] flex items-center gap-2">
        <Button variant="outline" onClick={() => setViewWeek(viewWeek - 1)}>
          <ChevronLeft />
        </Button>
        <Button variant="outline" onClick={() => setViewWeek(viewWeek + 1)}>
          <ChevronRight />
        </Button>
        <h2 className="px-4 text-3xl text-foreground">
          {format(weekDate, "MMMM yyyy")}
        </h2>
      </div>
      <div className="grid h-full w-full grid-cols-[75px_1fr] grid-rows-[75px_1fr] overflow-hidden">
        <div ref={topRef} className="col-start-2 col-end-3 overflow-x-hidden">
          <div
            style={{
              width: calWidth,
            }}
            className="grid h-full grid-cols-7 place-items-center items-end pb-2 text-muted-foreground"
          >
            {Array.from(Array(7).keys()).map((dayIndex) => {
              const currDate = setDay(weekDate, dayIndex)
              const isToday = isSameDay(new Date(), currDate)
              return (
                <div
                  key={dayIndex}
                  className={cn(
                    "whitespace-nowrap rounded-md px-5 py-2 text-center",
                    {
                      "bg-primary": isToday,
                      "text-primary-foreground": isToday,
                    },
                  )}
                >
                  <span>{format(currDate, "iii do")}</span>
                </div>
              )
            })}
          </div>
        </div>
        <div ref={sideRef} className="row-span-2 mr-2 overflow-y-hidden">
          <div
            style={{
              height: calHeight,
            }}
            className="grid grid-rows-[repeat(24,1fr)]"
          >
            {Array.from(Array(24).keys()).map((hour) => (
              <div
                className="-translate-y-[0.75em] text-right text-sm text-muted-foreground"
                key={hour}
              >
                {hour !== 0 && format(new Date().setHours(hour), "h aaa")}
              </div>
            ))}
          </div>
        </div>

        <div
          onScroll={(e) => {
            sideRef.current?.scrollTo(0, e.currentTarget.scrollTop)
            topRef.current?.scrollTo(e.currentTarget.scrollLeft, 0)
          }}
          ref={scrollRef}
          className={cn(
            "grid h-full w-full grid-cols-[repeat(7,minmax(100px,1fr))] overflow-auto border",
            className,
          )}
        >
          {Array.from(Array(7).keys()).map((dayIndex) => {
            return (
              <DayCol
                date={setDay(weekDate, dayIndex)}
                key={dayIndex}
                highlightedIntervals={highlightedIntervals}
              />
            )
          })}
        </div>
      </div>
    </div>
  )
}

interface DayCol {
  style?: React.CSSProperties
  className?: string
  date: Date
  highlightedIntervals: Interval[]
}
function DayCol({ className, style, highlightedIntervals, date }: DayCol) {
  return (
    <div
      style={style}
      className={cn("grid grid-rows-[repeat(24,1fr)] border", className)}
    >
      {Array.from(Array(24).keys()).map((hourIndex) => {
        const startHour = setHours(date, hourIndex)
        const endHour = setHours(date, hourIndex + 1)
        return (
          <div
            key={hourIndex}
            className={cn("min-h-[75px] border", {
              "bg-primary": highlightedIntervals.some((interval) =>
                areIntervalsOverlapping(
                  { start: startHour, end: endHour },
                  interval,
                ),
              ),
            })}
          />
        )
      })}
    </div>
  )
}
