import { HTTPProfileService } from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import LoadingSpinner from "./loadingSpinner"
import { X } from "lucide-react"
import { Button } from "./ui/button"
import toast from "react-hot-toast"
import { cn, getErrorMessage } from "@/lib/utils"
import { useState } from "react"
const profileService = new HTTPProfileService()

export interface documentImgInterface {
  documentId: string
  isAccount: boolean
  className?: string
}

export interface documentInterface {
  document: string
}

export default function DocumentImg({
  documentId,
  isAccount,
  className,
}: documentImgInterface) {
  //deleteOwnUserProfile needs to grab the id of the profile we are on
  const queryClient = useQueryClient()
  const [deleted, setDeleted] = useState<boolean>()

  const { data } = useQuery({
    queryKey: ["documents", documentId],
    queryFn: async () => {
      try {
        const data = await profileService.getDocument(documentId)
        console.log(data)
        if (!data.document.startsWith("data:")) setDeleted(true)
        return data
      } catch (error) {
        setDeleted(true)
        return {}
      }
    },
  })
  const deletion = async () => {
    try {
      setDeleted(true)
      const data = await profileService.deleteDocument(documentId)
      console.log(data)
      queryClient.invalidateQueries(["documents"])
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  if (!data) {
    return <LoadingSpinner />
  } else if ((data as documentInterface).document) {
    if (deleted) {
      ;(data as documentInterface).document = "unknown"
      return
    }
    return (
      <div
        className={cn(
          "my-5 flex h-[55rem] w-full shrink-0 flex-col-reverse items-end md:flex-row md:items-start",
          className,
        )}
      >
        <iframe
          src={(data as documentInterface).document}
          className="h-full w-full grow rounded border-2 border-inherit"
        />
        {isAccount && (
          <>
            <Button variant="ghost" className="h-9 w-10 p-0" onClick={deletion}>
              <X color="red" />
            </Button>
          </>
        )}
      </div>
    )
  }
}
