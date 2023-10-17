import { Input } from "./ui/input"

interface IconInputProps extends React.ComponentProps<typeof Input> {
  children: React.ReactNode
}
export default function IconInput({ children, ...props }: IconInputProps) {
  return (
    <div className="relative flex items-center gap-2">
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-foreground">
        {children}
      </div>
      <Input {...props} className="text-md pl-11" />
    </div>
  )
}
