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


  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" className="m-3 p-6">
          View Documents
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-5xl overflow-auto max-h-[53%]">
        <DialogHeader>
          <DialogTitle> Documents </DialogTitle>
          <DialogDescription className="flex gap-4 flex-wrap ">
            {documentIds.map((tId) => (
              <DocumentImg key={tId} documentId={tId} />
            ))}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
