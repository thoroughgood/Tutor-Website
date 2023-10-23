import { Controller, useForm } from "react-hook-form"
import { PopoverContent, Popover, PopoverTrigger } from "./ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Calendar } from "./ui/calendar"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"
import { CalendarIcon } from "lucide-react"
import { format, setMinutes, startOfDay } from "date-fns"
import { flatten, parseInt, range } from "lodash"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"

const zodSchema = z
  .object({
    date: z.date(),
    startTime: z.string().regex(/^[0-9]{2}:[0-9]{2} [A|P]M$/),
    endTime: z.string().regex(/^[0-9]{2}:[0-9]{2} [A|P]M$/),
  })
  .partial()
  .refine(
    ({ startTime, endTime }) => {
      if (startTime && endTime) {
        return (
          processTimeInputToDate(new Date(), startTime) <
          processTimeInputToDate(new Date(), endTime)
        )
      }
      return true
    },
    { message: "Start time should be before End time", path: ["date"] },
  )

const processTimeInputToDate = (date: Date, time: string) => {
  const [_, hour, minute, meridiem] = time.match(
    /^([0-9]{2}):([0-9]{2}) ([A|P]M)/,
  ) as RegExpMatchArray
  return setMinutes(
    startOfDay(date),
    (parseInt(hour) + meridiem === "PM" ? 12 : 0) + parseInt(minute),
  )
}

export default function EditAppointmentForm() {
  const {
    control,
    handleSubmit,
    getValues,
    setError,
    formState: { errors },
  } = useForm<z.infer<typeof zodSchema>>({
    resolver: zodResolver(zodSchema),
    reValidateMode: "onChange",
  })
  const onSubmit = ({
    date,
    startTime,
    endTime,
  }: z.infer<typeof zodSchema>) => {
    console.log("suibmit")
    // const startTimeDate = processTimeInputToDate(date, startTime)
    // const endTimeDate = processTimeInputToDate(date, endTime)
    // if (startTimeDate >= endTimeDate) {
    //   setError("endTime", {
    //     message: "End time should be greater than start time.",
    //   })
    // }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        control={control}
        name="date"
        render={({ field }) => (
          <Popover>
            <pre>{JSON.stringify(errors, null, 2)}</pre>
            <PopoverTrigger asChild>
              <Button variant={"outline"} className={cn()}>
                <CalendarIcon className="mr-2 h-4 w-4" />
                {field.value ? (
                  format(field.value, "PPP")
                ) : (
                  <span>Pick a date</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0">
              <Calendar
                mode="single"
                selected={field.value}
                onSelect={(date) => field.onChange(date)}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        )}
      />
      {["startTime", "endTime"].map((inputName) => (
        <Controller
          key={inputName}
          control={control}
          name={inputName as "startTime" | "endTime"}
          render={({ field }) => (
            <Select onValueChange={field.onChange}>
              <SelectTrigger className="w-fit">
                <SelectValue placeholder="Time" />
              </SelectTrigger>
              <SelectContent className="max-h-[300px]">
                {flatten(
                  range(24).map((hour) =>
                    range(0, 60, 15).map((minute) => {
                      let date = startOfDay(new Date())
                      date = setMinutes(date, hour * 60 + minute)
                      const formattedTime = format(date, "hh:mm aa")
                      return (
                        <SelectItem value={formattedTime} key={formattedTime}>
                          {formattedTime}
                        </SelectItem>
                      )
                    }),
                  ),
                )}
              </SelectContent>
            </Select>
          )}
        />
      ))}

      <Button type="submit">submit</Button>
    </form>
  )
}
