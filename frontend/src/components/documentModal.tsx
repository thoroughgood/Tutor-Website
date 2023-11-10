import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog"
import { useEffect, useState } from "react"
import useUser from "@/hooks/useUser"
import { Button } from "./ui/button"
import { HTTPProfileService } from "@/service/profileService"
import { useRouter } from "next/router"
import DocumentImg from "./documentImg"
import { Form, FormControl, FormField, FormItem, FormMessage } from "./ui/form"
import { Label } from "@radix-ui/react-label"
import { Input } from "./ui/input"
import { getErrorMessage } from "@/lib/utils"
import { fileToDataUrl } from "@/service/helpers"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import toast from "react-hot-toast"
import { z } from "zod"
import LoadingButton from "./loadingButton"
import { useQueryClient } from "react-query"
const profileService = new HTTPProfileService()

const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

const formSchema = z.object({
  document: z
    .any()
    .refine(
      (files) => ACCEPTED_FILE_TYPES.includes(files.type) || files == "",
      "Not accepted file type",
    ),
})

export interface documentModalInterface {
  documentIds: string[]
}

export default function DocumentModal({ documentIds }: documentModalInterface) {
  //here we are going to generate documentImg depending on the number of ids we have
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const tutorId = router.query.tutorId as string
  const [submitLoading, setSubmitLoading] = useState(false)
  const { user, setUser } = useUser()
  //we need to do for each item in documentIds -> render a new one given document id as a key and passing it in as a parameter

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log("hey")
    console.log(values)
    try {
      let doc = ""
      if (values.document.length != 0) {
        console.log(values.document)
        doc = (await fileToDataUrl(values.document)) as string
      }
      const docResponse = await profileService.uploadDocument(doc)
      queryClient.invalidateQueries(["tutors", tutorId])
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  useEffect(() => {
    form.setValue("document", "")
  }, [form])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" className="m-3 p-6">
          View Documents
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[53%] max-w-5xl overflow-auto">
        <DialogHeader>
          <DialogTitle> Documents </DialogTitle>
          <DialogDescription className="flex flex-wrap gap-4 ">
            <Form {...form}>
              <form
                className="flex flex-col gap-4 "
                onSubmit={form.handleSubmit(onSubmit)}
                noValidate
              >
                <FormField
                  control={form.control}
                  name="document"
                  render={({ field }) => (
                    <FormItem>
                      <Label>Document Upload</Label>
                      <FormControl>
                        <Input
                          type="file"
                          onChange={(e) => {
                            e.preventDefault()
                            if (e.target.files) {
                              field.onChange(e.target.files[0])
                            }
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <LoadingButton
                  role="submit"
                  className="w-3/12"
                  isLoading={submitLoading}
                >
                  Submit Changes
                </LoadingButton>
              </form>
            </Form>
            {documentIds.map((tId) => (
              <DocumentImg key={tId} documentId={tId} />
            ))}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter />
      </DialogContent>
    </Dialog>
  )
}
