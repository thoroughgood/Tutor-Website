import { HTTPProfileService } from "@/service/profileService"
import { useQuery, useQueryClient } from "react-query"
import LoadingSpinner from "./loadingSpinner"
import { X } from "lucide-react"
import { Button } from "./ui/button"
import toast from "react-hot-toast"
import { getErrorMessage } from "@/lib/utils"
import { useState } from "react"
const profileService = new HTTPProfileService()

export interface documentImgInterface {
  documentId: string
}

export default function DocumentImg({ documentId }: documentImgInterface) {
  //deleteOwnUserProfile needs to grab the id of the profile we are on
  const queryClient = useQueryClient()
  const [deleted, setDeleted] = useState(false)

  const { data } = useQuery({
    queryKey: ["documents", documentId],
    queryFn: async () => {
      const data = await profileService.getDocument(documentId)
      if (data) return data
    },
  })
  const deletion = async () => {
    try {
      const data = await profileService.deleteDocument(documentId)
      console.log(data)
      queryClient.invalidateQueries(["documents"])
      setDeleted(true)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  if (!data) {
    return <LoadingSpinner />
  } else if (data.document) {
    if (deleted) {
      data.document = "deleted"
      return <></>
    }
    return (
      <div className="mt-5 flex h-1/2 w-5/6 shrink-0">
        <iframe
          src={data.document}
          className="h-full w-full rounded border-2 border-inherit"
        />
        <Button variant="ghost" className="h-9 w-10 p-0" onClick={deletion}>
          <X color="red" />
        </Button>
      </div>
    )
  }
}
