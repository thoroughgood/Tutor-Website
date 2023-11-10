import { HTTPProfileService } from "@/service/profileService"
import { useQuery } from "react-query"
import LoadingSpinner from "./loadingSpinner"
const profileService = new HTTPProfileService()

export interface documentImgInterface {
  documentId: string
}

export default function DocumentImg({ documentId }: documentImgInterface) {
  //deleteOwnUserProfile needs to grab the id of the profile we are on
  const { data } = useQuery({
    queryKey: ["documentId", documentId],
    queryFn: () => profileService.getDocument(documentId),
  })

  if (!data) {
    return <LoadingSpinner />
  } else if (data.document) {
    return <iframe src={data.document} className="w-3/10 h-96" />
  }
}
