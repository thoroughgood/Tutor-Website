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
import { UseFormReturn, useForm } from "react-hook-form"
import * as z from "zod"
import { Input } from "@/components/ui/input"

import { Label } from "@/components/ui/label"
import { useEffect, useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { getErrorMessage } from "@/lib/utils"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"
import {
  HTTPProfileService,
  TutorSelfEditReqBody,
} from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import { Textarea } from "@/components/ui/textarea"
import toast from "react-hot-toast"

import { zodResolver } from "@hookform/resolvers/zod"
import Link from "next/link"
import DeleteModal from "@/components/deleteModal"
import EditOfferings from "@/components/editOfferings"
import { fileToDataUrl } from "@/service/helpers"

const authService = new HTTPAuthService()

const ACCEPTED_IMAGE_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/webp",
]

//null if the string value is empty
const formSchema = z.object({
  name: z
    .string()
    .min(1, {
      message: "Name is too short",
    })
    .max(50),
  bio: z.string(),
  profilePicture: z
    .any()
    .refine(
      (files) => ACCEPTED_IMAGE_TYPES.includes(files.type) || files == "",
      "Not accepted image type",
    ),
  location: z.string(),
  phoneNumber: z.string(),
  courseOfferings: z.array(
    z.object({
      name: z.string(),
    }),
  ),
})
const profileService = new HTTPProfileService()
export default function Edit() {
  const queryClient = useQueryClient()
  const router = useRouter()
  const { user } = useUser()
  const tutorId = router.query.tutorId as string
  const isOwnProfile = tutorId === user?.userId
  const [submitLoading, setSubmitLoading] = useState(false)

  const { data, isError } = useQuery({
    queryKey: ["tutors", tutorId],
    queryFn: () => profileService.getTutorProfile(tutorId),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
    staleTime: 1000 * 60 * 5,
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
      form.setValue("profilePicture", "")
    }
  }, [data, form])
  //if the user is a tutor or student and it's not their profile they dont have access. Admins always have access
  if (
    (user?.userType === "tutor" || user?.userType === "student") &&
    !isOwnProfile
  ) {
    return <div>You do not have access to this webpage</div>
  }

  if (!data) {
    return (
      <div className="grid h-full w-full  place-content-center overflow-hidden p-16">
        Loading Screen
      </div>
    )
  }

  const courses: string[] = []

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setSubmitLoading(true)

    try {
      values.courseOfferings.forEach((course) => {
        courses.push(course.name)
      })

      //need to manipulate profile value
      let file = ""
      if (values.profilePicture.length != 0) {
        file = (await fileToDataUrl(values.profilePicture)) as string
      }

      const tutorObj: TutorSelfEditReqBody = {
        name: values.name,
        bio: values.bio,
        email: data.email,
        profilePicture: file,
        location: values.location,
        phoneNumber: values.phoneNumber,
        courseOfferings: courses,
        timesAvailable: data.timesAvailable,
      }

      if (values.phoneNumber.length === 0) {
        tutorObj.phoneNumber = null
      }
      if (values.location.length === 0) {
        tutorObj.location = null
      }
      if (values.profilePicture.length === 0) {
        tutorObj.profilePicture = null
      }
      let response
      if (user?.userType === "admin") {
        tutorObj.id = tutorId
        response = await profileService.setOwnTutorProfile(tutorObj)
      } else {
        response = await profileService.setOwnTutorProfile(tutorObj)
      }

      if (response.success) {
        router.push(`/tutor/${router.query.tutorId as string}/`)
      }
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    queryClient.invalidateQueries({ queryKey: ["tutors", tutorId] })
    setSubmitLoading(false)
  }

  if (isError) {
    // Handle error here
    return <div>Error screen</div>
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
              <FormField
                control={form.control}
                name="profilePicture"
                render={({ field }) => (
                  <FormItem>
                    <Label>Profile Picture</Label>
                    <FormControl>
                      <Input
                        type="file"
                        onChange={(e) => {
                          e.preventDefault()
                          if (e.target.files) {
                            field.onChange(e.target.files[0])
                          }
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
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
              <EditOfferings form={form} />
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
          <Link href={`../${tutorId}`}> Back </Link>
        </Button>
        <DeleteModal profileId={tutorId} accountType="tutor" />
      </div>
    </div>
  )
}

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
