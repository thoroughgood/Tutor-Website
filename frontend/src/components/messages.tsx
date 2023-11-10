import { Message } from "@/service/messageService"
import { Card } from "./ui/card"
import { Input } from "./ui/input"
import { useState } from "react"
import useUser from "@/hooks/useUser"
import { cn } from "@/lib/utils"
import { Button } from "./ui/button"
import { SendIcon } from "lucide-react"

interface MessagesProps {
  className?: string
  messages: (Message | OptimisticMessage)[]
  sendMessage: (content: string) => void
  header: React.ReactNode
}
export interface OptimisticMessage
  extends Omit<Message, "sentTime" | "sentBy"> {
  isOptimistic: true
}
export default function Messages({
  className,
  messages,
  sendMessage,
  header,
}: MessagesProps) {
  const [input, setInput] = useState("")
  const { user } = useUser()
  return (
    <Card className={cn("flex flex-col gap-4 overflow-hidden p-4", className)}>
      {header}
      <hr />
      <div className="flex flex-col-reverse gap-0.5 overflow-y-scroll scrollbar-thin">
        {messages.toReversed().map((m) => (
          <div
            key={m.id}
            className={cn(
              "mr-8 inline self-start rounded border bg-secondary p-2 px-3 text-secondary-foreground",
              ("isOptimistic" in m || user?.userId === m.sentBy) &&
                "ml-8 mr-0 self-end bg-primary text-primary-foreground",
              "isOptimistic" in m && "opacity-50",
            )}
          >
            {m.content}
          </div>
        ))}
      </div>
      <div className="relative flex grow items-end ">
        <Input
          className="bg-secondary pr-16"
          placeholder="Send a message"
          autoFocus
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyUp={(e) => {
            if (e.key === "Enter" && input.length > 0) {
              sendMessage(input)
              setInput("")
            }
          }}
        />
        <Button
          className="absolute bottom-0 right-0 scale-95"
          variant="secondary"
          onClick={() => {
            if (input.length > 0) {
              sendMessage(input)
              setInput("")
            }
          }}
        >
          <SendIcon className="text-secondary-foreground" />
        </Button>
      </div>
    </Card>
  )
}
