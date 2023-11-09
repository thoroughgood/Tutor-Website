import { useState } from "react"
import useUser from "@/hooks/useUser"
import { HTTPProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import { useQuery } from "react-query"
import LoadingSpinner from "./loadingSpinner"
import { Document, Page } from "react-pdf"
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
    return (<LoadingSpinner />)
  } else if (data.document) {
    console.log(data.document)
    return <iframe src={data.document} className="h-96 w-3/10"/>
  }




  //need to import something to read the pdf files
}
