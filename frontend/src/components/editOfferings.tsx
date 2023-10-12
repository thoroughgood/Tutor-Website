import { useFieldArray, useForm } from "react-hook-form"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { cn } from "@/lib/utils"
import { X } from "lucide-react"
import { Button } from "./ui/button"
import { Input } from "./ui/input"

const formSchema = z.object({
  courseOfferings: z.array(
    z.object({
      name: z.string(),
    }),
  ),
})

export default function EditOfferings() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  const { fields, append, remove } = useFieldArray({
    name: "courseOfferings",
    control: form.control,
  })
  return (
    <>
      {fields.map((field, index) => (
        <FormField
          control={form.control}
          key={field.id}
          name={`courseOfferings.${index}.name`}
          render={({ field }) => (
            <div className="w-full items-center space-x-2">
              <FormItem>
                <FormLabel className={cn(index !== 0 && "grid-span sr-only")}>
                  Course Offerings
                </FormLabel>
                <FormControl>
                  <div className="flex items-center gap-2">
                    <Input {...field} />
                    <Button variant="destructive" onClick={() => remove(index)}>
                      <X />
                    </Button>
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            </div>
          )}
        />
      ))}
      <div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-2"
          onClick={() => append({ value: "" })}
        >
          Add Course Offerings
        </Button>
      </div>
    </>
  )
}
