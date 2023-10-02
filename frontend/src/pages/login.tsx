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
import { Button } from "@/components/ui/button"

import Link from "next/link"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import LoadingButton from "@/components/loadingButton"
import { HTTPAuthService } from "@/service/authService"
import { getErrorMessage } from "@/lib/utils"
import toast from "react-hot-toast"

const formSchema = z.object({
  name: z
    .string()
    .min(1, {
      message: "Enter your username",
    })
    .max(50),
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
export default function Login() {
  //defining a form, the zod object converts the standard format into a json readable format for the backend
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setSubmitLoading(true)
    try {
      const id = await authService.login(values)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    setSubmitLoading(false)
  }
  return (
    <Card className="w-screen max-w-md">
      <CardHeader className="text-center">
        <CardTitle>Login</CardTitle>
        <CardDescription>Login to your account.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            className="flex flex-col gap-4"
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
          >
            <CustomFormField form={form} name="name" label="Username" />
            <CustomFormField
              name="password"
              form={form}
              label="Password"
              inputType="password"
            />
            <div className="mt-4">
              <LoadingButton
                role="login"
                className="w-full"
                isLoading={submitLoading}
              >
                Login
              </LoadingButton>
              <Button asChild variant="link" className="px-0">
                <Link href={"/register"}>Register instead</Link>
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
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
