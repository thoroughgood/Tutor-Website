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

export default function editOfferings({ form, fields, remove, append }) {
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
        onClick={() => append({ value: "" })}
      >
        Add Course Offerings
      </Button>
    </div>
  )
}
