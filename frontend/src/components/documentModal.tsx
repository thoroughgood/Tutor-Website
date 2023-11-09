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
import DocumentImg from "./documentImg"
const profileService = new HTTPProfileService()

export interface documentModalInterface {
  documentIds: string[]
}

export default function DocumentModal({ documentIds }: documentModalInterface) {
  //here we are going to generate documentImg depending on the number of ids we have
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()

  //we need to do for each item in documentIds -> render a new one given document id as a key and passing it in as a parameter

  const deleteProfile = async () => {
    setSubmitLoading(true)
    try {
      //if student vs if tutor
      const deletion =
        user && user.userType === "student"
          ? await profileService.deleteOwnStudentProfile(profileId)
          : await profileService.deleteOwnTutorProfile(profileId)
    } catch {
      toast.error(getErrorMessage(Error))
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" className="m-3 p-6">
          View Documents
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle> Documents </DialogTitle>
          <DialogDescription>
            {documentIds.map((tId) => (
              <DocumentImg key={tId} documentId={tId} />
            ))}
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
              if (await toastProtectedFnCall(() => authService.logout())) {
                setUser(null)
                router.push("/register")
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
