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
import { getErrorMessage, toastProtectedFnCall } from "@/lib/utils"
import useUser from "@/hooks/useUser"
import { Button } from "./ui/button"
import { HTTPProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import { Input } from "./ui/input"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm, Form } from "react-hook-form"
const profileService = new HTTPProfileService()

const formSchema = z.object({
  password: z.string().min(8, {
    message: "Password is too short",
  }),
})

export interface deleteModalInterface {
  profileId: string
  accountType: "student" | "tutor"
}

export default function ResetModal({
  profileId,
  accountType,
}: deleteModalInterface) {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  //deleteOwnUserProfile needs to grab the id of the profile we are on

  const onSubmit = async () => {
    console.log(profileId)
    setSubmitLoading(true)
    try {
    } catch {
      toast.error(getErrorMessage(Error))
    }
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
              className="flex flex-col gap-4 "
              onSubmit={form.handleSubmit(onSubmit)}
              noValidate
            >
              <Input type="password" />
            </form>
          </Form>
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
            onClick={async () => {
              await deleteProfile()
              setOpen(false)
              setSubmitLoading(false)
              if (user?.userType !== "admin") {
                if (await toastProtectedFnCall(() => authService.logout())) {
                  setUser(null)
                  router.push("/register")
                }
              } else {
                router.push(`../../findUser`)
              }
            }}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
