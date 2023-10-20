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
import { MockProfileService } from "@/service/profileService"
import toast from "react-hot-toast"
import { getErrorMessage } from "@/lib/utils"
import useUser from "@/hooks/useUser"
import { Button } from "./ui/button"
const profileService = new MockProfileService()

export interface deleteModalInterface {
  profileId: string
}

export default function DeleteModal({ profileId }: deleteModalInterface) {
  const [open, setOpen] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user } = useUser()
  //deleteOwnUserProfile needs to grab the id of the profile we are on

  const deleteProfile = async () => {
    setSubmitLoading(true)
    try {
      const deletion = await profileService.deleteOwnUserProfile(profileId)
    } catch {
      toast.error(getErrorMessage)
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
            type="submit"
            onClick={() => {
              setOpen(false)
            }}
          >
            Cancel
          </Button>
          <LoadingButton
            variant="destructive"
            type="submit"
            isLoading={submitLoading}
            onClick={async () => {
              await deleteProfile()
              setOpen(false)
              setSubmitLoading(false)
            }}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
