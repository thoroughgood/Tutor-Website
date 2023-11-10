import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog"
import LoadingButton from "./loadingButton"
import { useState } from "react"
import toast from "react-hot-toast"
import { getErrorMessage } from "@/lib/utils"
import useUser from "@/hooks/useUser"
import { Button } from "./ui/button"
import { HTTPProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm, UseFormReturn } from "react-hook-form"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "./ui/form"
import { Input } from "./ui/input"
import { Label } from "./ui/label"

const profileService = new HTTPProfileService()

const formSchema = z.object({
  newPassword: z.string().min(8, {
    message: "Password is too short",
  }),
})

export interface resetModalInterface {
  profileId: string
}

export default function ResetModal({ profileId }: resetModalInterface) {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  //deleteOwnUserProfile needs to grab the id of the profile we are on

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log(profileId)
    setSubmitLoading(true)
    try {
      console.log(values)
      const response = await profileService.resetPassword(
        values.newPassword,
        profileId,
      )
      if (response.success) {
        toast.success("Password changed")
      }
    } catch {
      toast.error(getErrorMessage(Error))
    }
    setOpen(false)
    setSubmitLoading(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" className="m-3 p-6">
          Reset Password
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle> Reset Password </DialogTitle>
          <DialogDescription>
            This will reset the users password. Enter the user&apos;s new
            desired password
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Form {...form}>
            <form
              className="flex flex-row items-center gap-4"
              onSubmit={form.handleSubmit(onSubmit)}
              noValidate
            >
              <FormField
                control={form.control}
                name="newPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input {...field} type="string" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="grid grid-cols-2 gap-2 ">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setOpen(false)
                  }}
                >
                  Cancel
                </Button>
                <LoadingButton
                  variant="destructive"
                  isLoading={submitLoading}
                  role="submit"
                >
                  Reset
                </LoadingButton>
              </div>
            </form>
          </Form>
        </DialogFooter>
      </DialogContent>
    </Dialog>
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
