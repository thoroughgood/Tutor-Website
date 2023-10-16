import React from "react"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { cn } from "@/lib/utils"
import { X } from "lucide-react"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import {
  FieldArrayWithId,
  UseFieldArrayAppend,
  UseFieldArrayRemove,
  UseFormReturn,
} from "react-hook-form"
import { z } from "zod"
const formSchema = z.object({
  name: z
    .string()
    .min(1, {
      message: "Name is too short",
    })
    .max(50),
  bio: z.string(),
  profilePicture: z.string(),
  location: z.string(),
  phoneNumber: z.string(),
  courseOfferings: z.array(
    z.object({
      name: z.string(),
    }),
  ),
})
interface editOfferingsProps {
  form: UseFormReturn<z.infer<typeof formSchema>, any, undefined>
  fields: FieldArrayWithId<
    z.infer<typeof formSchema>,
    "courseOfferings",
    "id"
  >[]
  append: UseFieldArrayAppend<z.infer<typeof formSchema>, "courseOfferings">
  remove: UseFieldArrayRemove
}
export default function editOfferings({
  form,
  fields,
  remove,
  append,
}: editOfferingsProps) {
  return (
    <div>
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
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-2"
        onClick={() => append({ name: "" })}
      >
        Add Course Offerings
      </Button>
    </div>
  )
}
