import { Control, Controller, useForm } from "react-hook-form"
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
    globalErrors: z.string().optional(), // ts bandaid fix for global errors with zod resolver/refine
    date: z.date(),
    startTime: z.string().regex(/^[0-9]{2}:[0-9]{2} [A|P]M$/),
    endTime: z.string().regex(/^[0-9]{2}:[0-9]{2} [A|P]M$/),
  })
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
    {
      message: "Start time should be before end time",
      path: ["globalErrors"],
    },
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
    mode: "onChange",
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
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-2">
      <div className="flex gap-2">
        <div className="flex flex-col">
          <Controller
            control={control}
            name="date"
            render={({ field }) => (
              <Popover>
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
          {errors.date && <div>{errors.date.message}</div>}
        </div>
        <div className="flex flex-col">
          <TimeControlledInput
            control={control}
            name="startTime"
            placeholder="Start Time"
          />
          {errors.startTime && <div>{errors.startTime.message}</div>}
        </div>
        <div className="flex flex-col">
          <TimeControlledInput
            control={control}
            name="endTime"
            placeholder="End Time"
          />
          {errors.endTime && <div>{errors.endTime.message}</div>}
        </div>
      </div>
      {errors.globalErrors && <div>{errors.globalErrors.message}</div>}
      <Button type="submit">submit</Button>
    </form>
  )
}

interface TimeControlledInputProps {
  control: Control<z.infer<typeof zodSchema>>
  name: "startTime" | "endTime"
  placeholder: string
}
function TimeControlledInput({
  control,
  name,
  placeholder,
}: TimeControlledInputProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field }) => (
        <Select onValueChange={field.onChange}>
          <SelectTrigger className="w-fit">
            <SelectValue placeholder={placeholder} />
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
  )
}
