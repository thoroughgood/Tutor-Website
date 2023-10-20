import { cn } from "@/lib/utils"
import { useEffect, useRef, useState } from "react"
import {
  setDay,
  setWeek,
  format,
  getWeek,
  isSameDay,
  areIntervalsOverlapping,
  startOfDay,
  endOfDay,
  differenceInMinutes,
  startOfWeek,
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
  // Below required for scrolling the axis labels
  const [calHeight, setCalHeight] = useState(0)
  const [calWidth, setCalWidth] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)
  const topRef = useRef<HTMLDivElement>(null)
  const sideRef = useRef<HTMLDivElement>(null)

  const [viewWeek, setViewWeek] = useState(getWeek(new Date()))
  const [weekDate, setWeekDate] = useState(new Date())

  useEffect(() => {
    setWeekDate(startOfWeek(setWeek(new Date(), viewWeek)))
  }, [viewWeek])

  useEffect(() => {
    // This useEffect runs on component mount
    // It sets up window.resize event so that other variables/effects can rely on
    // the calendar width.
    // It also scrolls down to 7am by default
    const onResize = () => {
      setCalWidth(scrollRef.current?.scrollWidth || 0)
    }

    window.onresize = onResize
    if (scrollRef.current) {
      const height = scrollRef.current.scrollHeight
      setCalHeight(height)
      setCalWidth(scrollRef.current.scrollWidth)
      // scroll down to 7am for better UX
      scrollRef.current.scrollTo(0, (height / 24) * 7 + 10)
    }
    return () => window.removeEventListener("resize", onResize)
  }, [])

  return (
    <div className="flex h-full w-full flex-col gap-3 overflow-hidden">
      <div className="ml-[50px] flex items-center gap-2">
        {/* Calendar Controls */}
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
        {/* Calendar x-axis labels (i.e. day of the week) */}
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
          {/* Calendar y-axis labels (i.e. hours of the day) */}
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

        {/* Actual Calendar */}
        <div
          onScroll={(e) => {
            // Scrolling the x and y axis (necessary since we want them to be sticky as well)
            sideRef.current?.scrollTo(0, e.currentTarget.scrollTop)
            topRef.current?.scrollTo(e.currentTarget.scrollLeft, 0)
          }}
          ref={scrollRef}
          className={cn(
            "grid h-full w-full grid-cols-[repeat(7,minmax(100px,1fr))] overflow-auto border",
            className,
          )}
        >
          {/* Creating columns for each day */}
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

const MINUTES_IN_DAY = 60 * 24
interface DayColProps {
  style?: React.CSSProperties
  className?: string
  date: Date
  highlightedIntervals: Interval[]
}
function DayCol({ className, style, highlightedIntervals, date }: DayColProps) {
  const dayInterval = {
    start: startOfDay(date),
    end: endOfDay(date),
  }
  const colRef = useRef<HTMLDivElement>(null)
  const [colHeight, setColHeight] = useState(0)

  useEffect(() => {
    // This useEffect runs on component mount
    // sets initial column height and resize hook for other variabnles/effects to use
    setColHeight(colRef.current?.scrollHeight || 0)
    const onResize = () => {
      setColHeight(colRef.current?.scrollHeight || 0)
    }
    window.onresize = onResize
    return () => window.removeEventListener("resize", onResize)
  }, [])

  // remove any intervals that dont occur within this day
  highlightedIntervals = highlightedIntervals.filter((interval) =>
    areIntervalsOverlapping(dayInterval, interval),
  )

  // little bit of math to calculate x offset and height of absolute positioned interval elements
  const intervalElements = highlightedIntervals.map((interval) => {
    const startY =
      (differenceInMinutes(interval.start, startOfDay(date)) / MINUTES_IN_DAY) *
      colHeight
    const height =
      (differenceInMinutes(interval.end, interval.start) / MINUTES_IN_DAY) *
      colHeight

    return (
      <div
        key={interval.start.toString()}
        className="absolute w-full bg-green-600/90 p-2 text-sm font-bold text-green-50"
        style={{
          height,
          transform: `translateY(${startY}px)`,
        }}
      >
        {`${format(interval.start, "h:mmaaa")} – ${format(
          interval.end,
          "h:mmaaa",
        )}`}
      </div>
    )
  })
  return (
    <div
      ref={colRef}
      style={style}
      className={cn(
        "relative grid grid-rows-[repeat(24,1fr)] border",
        className,
      )}
    >
      {intervalElements}
      {Array.from(Array(24).keys()).map((hourIndex) => {
        return <div key={hourIndex} className={cn("min-h-[75px] border")} />
      })}
    </div>
  )
}
