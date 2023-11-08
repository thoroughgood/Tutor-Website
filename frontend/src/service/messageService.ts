import { nanoid } from "nanoid"
import { HTTPProfileService } from "./profileService"
interface MessageRawResp {
  id: string
  sentBy: string
  sentTime: string
  content: string
}

export interface Message extends Omit<MessageRawResp, "sentTime"> {
  sentTime: Date
}

interface MessageSentResp {
  id: string
  sentTime: Date
}

interface MessageService {
  getDirectChannelList(): Promise<string[]>
  getDirectMessages(otherUserId: string): Promise<Message[]>
  sendDirectMessage(
    otherUserId: string,
    content: string,
  ): Promise<MessageSentResp>
}

export class MockMessageService implements MessageService {
  private userId: string
  private messages: Message[]
  constructor(userId: string) {
    this.userId = userId
    this.messages = [
      {
        id: nanoid(),
        sentTime: new Date(2020, 4),
        sentBy: userId,
        content: "hi",
      },
      {
        id: nanoid(),
        sentTime: new Date(2020, 4, 1),
        sentBy: userId,
        content: "hi2 tjslkj sfsajf the quic rown fosx",
      },
      {
        id: nanoid(),
        sentTime: new Date(2020, 4, 1, 1),
        sentBy: "otheruserid",
        content: "i am another user!",
      },
    ]
  }
  async getDirectChannelList() {
    const profileService = new HTTPProfileService()
    const users = await profileService.searchTutors({})
    return users.tutorIds
  }
  async getDirectMessages(otherUserId: string) {
    return this.messages.map((m) => ({
      ...m,
      sentBy: m.sentBy === this.userId ? this.userId : otherUserId,
    }))
  }
  async sendDirectMessage(
    _otherUserId: string,
    content: string,
  ): Promise<MessageSentResp> {
    const newMessage = {
      id: nanoid(),
      sentTime: new Date(),
      sentBy: this.userId,
      content,
    }
    this.messages.push(newMessage)
    return {
      id: newMessage.id,
      sentTime: newMessage.sentTime,
    }
  }
}
