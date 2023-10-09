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

import { Label } from "@/components/ui/label"
import { useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { cn, getErrorMessage } from "@/lib/utils"
import { zodResolver } from "@hookform/resolvers/zod"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"
import { MockProfileService } from "@/service/profileService"
import { useQuery } from "react-query"
import { Textarea } from "@/components/ui/textarea"
import { X } from "lucide-react"
import toast from "react-hot-toast"

const authService = new HTTPAuthService()

//changed courseOfferings into an object -> have to then manipulate it to be an array upon data submission
//need to change
const formSchema = z.object({
  id: z.string(),
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
      name: z.string(),
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
    name: data?.name,
    bio: data?.bio,
    email: data?.email,
    location: data?.location,
    phoneNumber: data?.phoneNumber,
  }

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues,
  })

  const { fields, append, remove } = useFieldArray({
    name: "courseOfferings",
    control: form.control,
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  const courses: string[] = []
  const tester = () => {
    console.log("hello")
  }
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    //need to modify to convert from image to base64URI values.profilePicture
    console.log(1)
    setSubmitLoading(true)
    console.log("submitting")
    try {
      values.id = tutorId
      values.courseOfferings.forEach((e) => {
        courses.push(e.name)
      })
      for (const val in values) {
        if (val === "") {
          val === null
        }
      }

      const tutorObj = {
        id: tutorId,
        name: values.name,
        bio: values.bio,
        email: values.email,
        profilePicture: values.profilePicture,
        location: values.location,
        phoneNumber: values.phoneNumber,
        courseOfferings: courses,
        timeAvailable: data?.timeAvailable,
      }

      const id = await profileService.setTutorProfile(tutorId, tutorObj)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    setSubmitLoading(false)
  }

  const DeleteProfile = {}
  return (
    <div className="grid h-full w-full  place-content-center overflow-hidden p-16">
      <Card className="flex w-screen max-w-2xl flex-col overflow-y-auto">
        <CardHeader className=" text-center">
          <CardTitle>Edit Profile </CardTitle>
          <CardDescription>Change your details here!</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              className="flex flex-col gap-4 "
              onSubmit={form.handleSubmit(onSubmit)}
              noValidate
            >
              <CustomFormField form={form} name="name" label="Name" />
              <FormField
                control={form.control}
                name="bio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Bio</FormLabel>
                    <FormControl>
                      <Textarea className="resize-none" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <CustomFormField
                name="profilePicture"
                form={form}
                label="Profile Picture"
                inputType="file"
              />
              <div className="grid grid-cols-2 gap-3">
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
              </div>

              <div>
                {fields.map((field, index) => (
                  <FormField
                    control={form.control}
                    key={field.id}
                    name={`courseOfferings.${index}.name`}
                    render={({ field }) => (
                      <div className="w-full items-center space-x-2">
                        <FormItem>
                          <FormLabel
                            className={cn(index !== 0 && "grid-span sr-only")}
                          >
                            Course Offerings
                          </FormLabel>
                          <FormControl>
                            <div className="flex items-center gap-2">
                              <Input {...field} />
                              <Button
                                variant="destructive"
                                onClick={() => remove(index)}
                              >
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
              <div className=" mt-4">
                <LoadingButton
                  role="submit"
                  className="w-3/12"
                  isLoading={submitLoading}
                >
                  Submit Changes
                </LoadingButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
      <div className="p-auto relative mx-auto my-5 max-w-sm text-center">
        <Button asChild className="m-3 p-6" variant="secondary">
          <a href={`../${user?.userId}`}> Back </a>
        </Button>
      </div>
      <Button
        onClick={() => {
          DeleteProfile
        }}
      >
        Delete Profile
      </Button>
    </div>
  )

  interface CustomFormFieldProps {
    form: UseFormReturn<z.infer<typeof formSchema>, any, undefined>
    name: keyof z.infer<typeof formSchema>
    label: string
    inputType?: string
    defaultValue?: string
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
