import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form"
import { UseFormReturn, useForm } from "react-hook-form"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { Input } from "@/components/ui/input"

import { Label } from "@/components/ui/label"
import { useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { getErrorMessage } from "@/lib/utils"
import toast from "react-hot-toast"
import useUser from "@/hooks/useUser"
import { useRouter } from "next/router"

const formSchema = z.object({
  name: z
    .string()
    .min(1, {
      message: "Name is too short",
    })
    .max(50),
  email: z.string().email(),
  password: z.string().min(8, {
    message: "Password is too short",
  }), // TODO: refine this
  // confirmPassword: z.string(),
})
// .refine(({ password, confirmPassword }) => password == confirmPassword, {
//   message: "Passwords do not match",
//   path: ["confirmPassword"],
// })

// NOTE: confirm password decreases UX without much benefit to password input accuracy
// Commented out confirm passwords for better UX/UI

const authService = new HTTPAuthService()
export default function Register() {
  const router = useRouter()
  const { setUser } = useUser()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  type admin = {
    name: string
    email: string
    accountType: "admin"
    password: string
  }
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setSubmitLoading(true)
    try {
      const account: admin = {
        name: values.name,
        email: values.email,
        accountType: "admin",
        password: values.password,
      }
      const { id } = await authService.adminCreate(account)
      setUser({ userId: id, userType: account.accountType })
      toast("Account created")
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    setSubmitLoading(false)
  }
  return (
    <div className="grid h-full w-full  place-content-center overflow-hidden p-16">
      <Card className="w-screen max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Admin Generator</CardTitle>
          <CardDescription>Create a new admin account.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              className="flex flex-col gap-4"
              onSubmit={form.handleSubmit(onSubmit)}
              noValidate
            >
              <CustomFormField form={form} name="name" label="Full Name" />
              <CustomFormField
                name="email"
                form={form}
                inputType="email"
                label="Email"
              />
              <CustomFormField
                name="password"
                form={form}
                label="Password"
                inputType="password"
              />
              <div className="mt-4">
                <LoadingButton
                  role="submit"
                  className="w-full"
                  isLoading={submitLoading}
                >
                  Submit
                </LoadingButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}

// scary interface
interface CustomFormFieldProps {
  form: UseFormReturn<z.infer<typeof formSchema>, any, undefined>
  name: keyof z.infer<typeof formSchema>
  label: string
  inputType?: string
}

/**
 * Reusable basic custom form field
 */
function CustomFormField({
  label,
  form,
  name,
  inputType,
}: CustomFormFieldProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <Label>{label}</Label>
          <FormControl>
            <Input {...field} type={inputType} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  )
}
