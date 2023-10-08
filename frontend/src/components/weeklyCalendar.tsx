import { cn } from "@/lib/utils"
import { useEffect, useRef, useState } from "react"
import { setDay, format } from "date-fns"

interface WeeklyCalendarProps {
  className?: string
}
export default function WeeklyCalendar({ className }: WeeklyCalendarProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [calHeight, setCalHeight] = useState(0)
  const [calWidth, setCalWidth] = useState(0)
  const topRef = useRef<HTMLDivElement>(null)
  const sideRef = useRef<HTMLDivElement>(null)
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
    <div className="grid h-full w-full grid-cols-[50px_1fr] grid-rows-[50px_1fr]">
      <div ref={topRef} className="col-start-2 col-end-3 overflow-x-hidden">
        <div
          style={{
            width: calWidth,
          }}
          className="grid grid-cols-7 place-items-center text-muted-foreground"
        >
          {Array.from(Array(7).keys()).map((dayIndex) => (
            <div key={dayIndex} className="flex flex-col items-center">
              <span>{format(setDay(new Date(), dayIndex), "iii")}</span>
              <span>{format(setDay(new Date(), dayIndex), "d")}</span>
            </div>
          ))}
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
        {Array.from(Array(7).keys()).map((dayIndex) => (
          <DayCol key={dayIndex} />
        ))}
      </div>
    </div>
  )
}

interface DayCol {
  style?: React.CSSProperties
  className?: string
}
function DayCol({ className, style }: DayCol) {
  return (
    <div style={style} className={cn("grid grid-rows-[repeat(24,1fr)] border")}>
      {Array.from(Array(24).keys()).map((hourIndex) => (
        <div key={hourIndex} className="min-h-[75px] border" />
      ))}
    </div>
  )
}
