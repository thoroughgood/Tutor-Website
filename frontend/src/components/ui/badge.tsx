import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        random: "border-transparent",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, children, ...props }: BadgeProps) {
  let hashStyle = {}
  if (variant === "random") {
    const hashKey = JSON.stringify({
      child: children?.toString().toLowerCase(),
    })
      .split("")
      .reduce((prev, curr, i) => prev + curr.charCodeAt(0) * (i * 2), 0)
    const colorHue = hashKey % 255
    const bgColor = `hsl(${colorHue}, 100%, 93%)`
    const textColor = `hsl(${colorHue}, 100%, 30%)`
    hashStyle = {
      color: textColor,
      backgroundColor: bgColor,
      borderColor: `hsl(${colorHue}, 50%, 70%)`,
    }
  }

  return (
    <div
      style={hashStyle}
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    >
      {children}
    </div>
  )
}

export { Badge, badgeVariants }
