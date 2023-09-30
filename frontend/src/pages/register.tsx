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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
      message: "Name is too short",
    })
    .max(50),
  email: z.string().email(),
  accountType: z.enum(["tutor", "student"]),
  password: z.string().min(8, {
    message: "Password is too short",
  }), // TODO: refine this
  // confirmPassword: z.string(),
})
// .refine(({ password, confirmPassword }) => password == confirmPassword, {
//   message: "Passwords do not match",
//   path: ["confirmPassword"],
// })

// README: confirm password decreases UX without much benefit to password input accuracy
// Commented out confirm passwords for better UX/UI

const authService = new HTTPAuthService()
export default function Register() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setSubmitLoading(true)
    try {
      const id = await authService.register(values)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
    setSubmitLoading(false)
  }
  return (
    <Card className="w-screen max-w-md">
      <CardHeader className="text-center">
        <CardTitle>Register</CardTitle>
        <CardDescription>Create an account.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            className="flex flex-col gap-4"
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
          >
            <div className="grid grid-cols-2 items-end gap-4">
              <CustomFormField form={form} name="name" label="Full Name" />
              <FormField
                control={form.control}
                name="accountType"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Select onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select Account Type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="student">Student</SelectItem>
                          <SelectItem value="tutor">Tutor</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormMessage>
                      {/* We need this so the select box is 
                      aligned when name has an error */}
                      {form.getFieldState("name").invalid && "\xa0"}
                    </FormMessage>
                  </FormItem>
                )}
              />
            </div>
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
              <Button asChild variant="link" className="px-0">
                <Link href={"/login"}>Login instead</Link>
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
  form: UseFormReturn<
    {
      name: string
      email: string
      accountType: "tutor" | "student"
      password: string
    },
    any,
    undefined
  >
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
