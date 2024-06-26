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
import useUser from "@/hooks/useUser"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import router from "next/router"

//this is a template, z.object will condense the information parsed into it as a readable json format, and formaSchema is basically from the form

const formSchema = z.object({
  accountType: z.enum(["tutor", "student", "admin"]),
  email: z.string().email(),
  password: z.string(),
})

const authService = new HTTPAuthService()
export default function Login() {
  //defining a form, the zod object converts the standard format into a json readable format for the backend
  //z.infer checks the type and guesses how to do shit -> zodResolver finishes compilation type thing
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })
  //need to identify if it is loading for shadcn framework
  const [submitLoading, setSubmitLoading] = useState(false)
  //deconstructor
  const { setUser } = useUser()
  //when the form is submitted we call this async to submit the form
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setSubmitLoading(true)
    try {
      const { id } = await authService.login(values)
      setUser({
        userId: id,
        userType: values.accountType,
      })
      router.push("/appointments")
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
            <div className="grid grid-cols-2 items-end gap-4">
              <CustomFormField form={form} name="email" label="Email" />
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
                          <SelectItem value="admin">Admin</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    <FormMessage>
                      {/* We need this so the select box is 
                      aligned when name has an error */}
                      {form.getFieldState("email").invalid && "\xa0"}
                    </FormMessage>
                  </FormItem>
                )}
              />
            </div>
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
