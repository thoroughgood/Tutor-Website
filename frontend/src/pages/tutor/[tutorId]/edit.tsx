import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { UseFormReturn, useFieldArray, useForm } from "react-hook-form"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { cn, getErrorMessage } from "@/lib/utils"
import toast from "react-hot-toast"
import { ThemeToggle } from "@/components/themeToggle"
import { Toaster } from "react-hot-toast"
import { zodResolver } from "@hookform/resolvers/zod"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"
import { MockProfileService } from "@/service/profileService"
import { useQuery } from "react-query"

const authService = new HTTPAuthService()

//changed courseOfferings into an object -> have to then manipulate it to be an array upon data submission
const formSchema = z.object({
  name: z
    .string()
    .min(1, {
      message: "Name is too short",
    })
    .max(50),
  bio: z.string(),
  email: z.string(),
  profilePicture: z.string().optional(),
  location: z.string().optional(),
  phoneNumber: z.string().optional(),
  courseOfferings: z.array(
    z.object({
      name: z.string().regex(/^[A-z]{4}[0-9]{4}$/, {
        message: "Code does not fit course code format",
      }),
    }),
  ),
  timeAvailable: z
    .object({
      startTime: z.string(),
      endTime: z.string(),
    })
    .array(),
})
const profileService = new MockProfileService()
export default function Edit() {
  const router = useRouter()
  const { user } = useUser()
  const tutorId = router.query.tutorId as string
  const isOwnProfile = tutorId === user?.userId

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  const { fields, append } = useFieldArray({
    name: "courseOfferings",
    control: form.control,
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    //need to modify to convert from image to base64URI values.profilePicture
    setSubmitLoading(true)
    try {
      //will need to create a mock implementation of the edit api/return values
      //const id = await userService.edit(values)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    setSubmitLoading(false)
  }

  const { data } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: () => profileService.getTutorProfile(tutorId),
  })
  //create an empty array of objects
  const test: { name: string }[] = []

  //push in courses from profile
  data?.courseOfferings.forEach((course) => {
    test.push({ name: course })
  })

  const defaultValues: Partial<z.infer<typeof formSchema>> = {
    courseOfferings: test,
  }

  return (
    <div className="flex h-screen w-screen flex-row">
      <Toaster />
      <ThemeToggle />
      <div className="grid w-10/12 place-content-center">
        <Card className="w-screen max-w-md">
          <CardHeader className="text-center">
            <CardTitle>Edit Profile </CardTitle>
            <CardDescription>Change your details here!</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form
                className="flex flex-col gap-4"
                onSubmit={form.handleSubmit(onSubmit)}
                noValidate
              >
                <div className="grid grid-cols-2 items-end gap-4">
                  <CustomFormField form={form} name="name" label="Name" />
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Select onValueChange={field.onChange}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select Account Type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="student">Student</SelectItem>
                              <SelectItem value="tutor">Tutor</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage>
                          {/* We need this so the select box is 
                      aligned when name has an error */}
                          {form.getFieldState("name").invalid && "\xa0"}
                        </FormMessage>
                      </FormItem>
                    )}
                  />
                </div>
                <CustomFormField
                  name="bio"
                  form={form}
                  inputType="string"
                  label="Bio"
                />
                <CustomFormField
                  name="email"
                  form={form}
                  label="Email"
                  inputType="email"
                />
                <CustomFormField
                  name="profilePicture"
                  form={form}
                  label="Profile Picture"
                  inputType="file"
                />
                <CustomFormField
                  name="location"
                  form={form}
                  label="Location"
                  inputType="string"
                />
                <CustomFormField
                  name="phoneNumber"
                  form={form}
                  label="Phone Number"
                  inputType="string"
                />
                <div>
                  {fields.map((field, index) => (
                    <FormField
                      control={form.control}
                      key={field.id}
                      name={`courseOfferings.${index}.name`}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className={cn(index !== 0 && "sr-only")}>
                            Course Offerings
                          </FormLabel>
                          <FormDescription
                            className={cn(index !== 0 && "sr-only")}
                          >
                            Must be formatted
                          </FormDescription>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
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
                {/* come back to check on this -> need multiple inputs*/}
                <CustomFormField
                  name="timeAvailable"
                  form={form}
                  label="Available Times"
                  inputType="String"
                />

                <div className="mt-4">
                  <LoadingButton
                    role="submit"
                    className="w-full"
                    isLoading={submitLoading}
                  >
                    Submit Changes
                  </LoadingButton>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
      <div className="p-auto relative mx-auto my-5 max-w-sm text-center">
        <Button asChild className="m-3 p-6">
          <a href={`../${user?.userId}`}> Return to profile </a>
        </Button>
      </div>
    </div>
  )

  interface CustomFormFieldProps {
    form: UseFormReturn<z.infer<typeof formSchema>, any, undefined>
    name: keyof z.infer<typeof formSchema>
    label: string
    inputType?: string
    formDescription?: string
  }

  function CustomFormField({
    label,
    form,
    name,
    inputType,
    formDescription,
  }: CustomFormFieldProps) {
    return formDescription ? (
      <FormField
        control={form.control}
        name={name}
        render={({ field }) => (
          <FormItem>
            <Label>{label}</Label>
            <FormControl>
              <Input {...field} type={inputType} />
            </FormControl>
            <FormDescription>{formDescription}</FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    ) : (
      <FormField
        control={form.control}
        name={name}
        render={({ field }) => (
          <FormItem>
            <Label>{label}</Label>
            <FormControl>
              <Input {...field} type={inputType} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    )
  }
}
