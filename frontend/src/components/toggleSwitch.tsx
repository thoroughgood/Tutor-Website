import { cn } from "@/lib/utils"

interface ToggleSwitchProps {
  isToggled: boolean
  onClick?: React.MouseEventHandler<HTMLButtonElement>
  untoggledText: string
  toggledText: string
  className?: string
}

export default function ToggleSwitch({
  isToggled,
  onClick,
  untoggledText,
  toggledText,
  className,
}: ToggleSwitchProps) {
  const notchClasses = isToggled ? "translate-x-[100%]" : ""
  const toggledClasses = isToggled
    ? "text-background z-10"
    : "text-muted-foreground"
  const untoggleClasses = !isToggled
    ? "text-background z-10"
    : "text-muted-foreground"
  return (
    <button
      role="switch"
      aria-checked={isToggled}
      aria-roledescription="Toggle between states"
      className={cn("relative grid-cols-2 gap-x-4 rounded p-2", className)}
      onClick={onClick}
    >
      <div className="grid grid-cols-2 gap-x-4">
        <p
          aria-label="state 1"
          aria-selected={!isToggled}
          className={cn(untoggleClasses, "transition")}
        >
          {untoggledText}
        </p>
        <p
          aria-label="state 2"
          aria-selected={isToggled}
          className={cn(toggledClasses, "transiiton")}
        >
          {toggledText}
        </p>
      </div>
      <span
        aria-hidden
        data-testid="toggle-span"
        className={cn(
          "absolute left-1 top-1.5 h-[calc(100%-10px)] w-[calc(50%-5px)] rounded bg-primary text-black transition-all",
          notchClasses,
        )}
      />
    </button>
  )
}
