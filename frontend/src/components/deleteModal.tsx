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
import { HTTPAuthService } from "@/service/authService"
import { useRouter } from "next/router"
const profileService = new HTTPProfileService()
const authService = new HTTPAuthService()

export interface deleteModalInterface {
  profileId: string
  accountType: "student" | "tutor"
}

export default function DeleteModal({
  profileId,
  accountType,
}: deleteModalInterface) {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()

  //deleteOwnUserProfile needs to grab the id of the profile we are on

  const deleteProfile = async () => {
    console.log(profileId)
    setSubmitLoading(true)
    try {
      if (accountType === "student") {
        const response = await profileService.deleteOwnStudentProfile(profileId)
        console.log(response)
      }
      if (accountType === "tutor") {
        const response = await profileService.deleteOwnTutorProfile(profileId)
        console.log(response)
      }
    } catch {
      toast.error(getErrorMessage(Error))
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="destructive" className="m-3 p-6">
          Delete Profile
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle> Delete Profile </DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently remove your
            account and your data from our servers.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
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
                router.push(`../${profileId}`)
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
