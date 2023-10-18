import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-muted text-black text-opacity-0",
        className,
      )}
      {...props}
    />
  )
}

export { Skeleton }
