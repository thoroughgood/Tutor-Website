import { Loader2 } from "lucide-react"
import { Button } from "./ui/button"

interface LoadingButtonProps extends React.ComponentProps<typeof Button> {
  isLoading: boolean
  children: React.ReactNode
}
export default function LoadingButton({
  isLoading,
  children,
  ...props
}: LoadingButtonProps) {
  return (
    <Button {...props} disabled={isLoading}>
      {isLoading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Loading
        </>
      ) : (
        <>{children}</>
      )}
    </Button>
  )
}
