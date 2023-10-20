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
import { useEffect, useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { getErrorMessage } from "@/lib/utils"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"
import { MockProfileService } from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import { Textarea } from "@/components/ui/textarea"
import toast from "react-hot-toast"

import { zodResolver } from "@hookform/resolvers/zod"
import Link from "next/link"
import DeleteModal from "@/components/deleteModal"
import EditOfferings from "@/components/editOfferings"

const authService = new HTTPAuthService()

//null if the string value is empty
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
const profileService = new MockProfileService()
export default function Edit() {
  const queryClient = useQueryClient()
  const router = useRouter()
  const { user } = useUser()
  const tutorId = router.query.tutorId as string
  const isOwnProfile = tutorId === user?.userId
  const [submitLoading, setSubmitLoading] = useState(false)

  const { data } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: () => profileService.getTutorProfile(tutorId),
  })

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    if (data) {
      const courseObj: { name: string }[] = []

      //push in courses from profile
      data.courseOfferings.forEach((course) => {
        courseObj.push({ name: course })
      })

      form.setValue("name", data.name)
      form.setValue("bio", data.bio)
      form.setValue("location", data.location || "")
      form.setValue("phoneNumber", data.phoneNumber || "")
      form.setValue("courseOfferings", courseObj)
      form.setValue("profilePicture", data.profilePicture || "")
    }
  }, [data, form])

  const { fields, append, remove } = useFieldArray({
    name: "courseOfferings",
    control: form.control,
  })

  if (!data) {
    return <div> loading screen </div>
  }

  const courses: string[] = []

  type tutor = {
    id: string
    name: string
    bio: string
    email: string
    profilePicture: string | null
    location: string | null
    phoneNumber: string | null
    courseOfferings: string[]
    timeAvailable: {
      startTime: string
      endTime: string
    }[]
  }

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    //need to modify to convert from image to base64URI values.profilePicture
    setSubmitLoading(true)
    try {
      values.courseOfferings.forEach((course) => {
        courses.push(course.name)
      })

      const tutorObj: tutor = {
        id: tutorId,
        name: values.name,
        bio: values.bio,
        email: data?.email,
        profilePicture: values.profilePicture,
        location: values.location,
        phoneNumber: values.phoneNumber,
        courseOfferings: courses,
        timeAvailable: data?.timeAvailable,
      }

      if (values.phoneNumber === "") {
        tutorObj.phoneNumber = null
      }
      if (values.location === "") {
        tutorObj.location = null
      }
      if (values.profilePicture === "") {
        tutorObj.profilePicture = null
      }

      const id = await profileService.setOwnTutorProfile(tutorObj)
      const test = await profileService.getTutorProfile(tutorId)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    queryClient.invalidateQueries({ queryKey: ["tutors", tutorId] })
    setSubmitLoading(false)
  }
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
              <EditOfferings
                form={form}
                fields={fields}
                append={append}
                remove={remove}
              />
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
          <Link href={`../${user?.userId}`}> Back </Link>
        </Button>
        <DeleteModal profileId={tutorId} />
      </div>
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
