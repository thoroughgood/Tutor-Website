import { nanoid } from "nanoid"
import { HTTPProfileService } from "./profileService"
import { HTTPService } from "./helpers"
import wretch from "wretch"
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
  getAppointmentList(): Promise<string[]>
  sendDirectMessage(
    otherUserId: string,
    content: string,
  ): Promise<MessageSentResp>
  getAppointmentMessages(appointmentId: string): Promise<Message[]>
  sendAppointmentMessage(
    appointmentId: string,
    content: string,
  ): Promise<MessageSentResp>
}

export class HTTPMessageService extends HTTPService implements MessageService {
  async getDirectMessages(otherUserId: string): Promise<Message[]> {
    const resp = (await wretch(
      `${this.backendURL}/directmessage/${otherUserId}`,
    )
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
      .json()) as { messages: MessageRawResp[] }

    return resp.messages.map((m) => ({
      ...m,
      sentTime: new Date(m.sentTime),
    }))
  }

  async getDirectChannelList(): Promise<string[]> {
    const resp = wretch(`${this.backendURL}/directmessage/all`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    const respData: { otherIds: string[] } = await resp.json()
    return respData.otherIds
  }

  async sendDirectMessage(
    otherUserId: string,
    content: string,
  ): Promise<MessageSentResp> {
    const resp = (await wretch(`${this.backendURL}/directmessage/`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        otherId: otherUserId,
        message: content,
      })
      .post()
      .json()) as { id: string; sentTime: string }
    return { ...resp, sentTime: new Date(resp.sentTime) }
  }

  async getAppointmentList(): Promise<string[]> {
    const resp = (await wretch(
      `${this.backendURL}/appointments/?sortBy=messageSent`,
    )
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
      .json()) as { appointments: string[] }
    return resp.appointments
  }

  async getAppointmentMessages(appointmentId: string): Promise<Message[]> {
    const resp = (await wretch(
      `${this.backendURL}/appointment/${appointmentId}/messages`,
    )
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
      .json()) as { messages: MessageRawResp[] }

    return resp.messages.map((m) => ({
      ...m,
      sentTime: new Date(m.sentTime),
    }))
  }

  async sendAppointmentMessage(
    appointmentId: string,
    content: string,
  ): Promise<MessageSentResp> {
    const resp = (await wretch(`${this.backendURL}/appointment/message`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        id: appointmentId,
        message: content,
      })
      .post()
      .json()) as { id: string; sentTime: string }
    return { ...resp, sentTime: new Date(resp.sentTime) }
  }
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
  async getAppointmentList(): Promise<string[]> {
    throw new Error("not implemented")
  }

  async sendAppointmentMessage(
    _appointmentId: string,
    _otherUserIdcontent: string,
  ): Promise<MessageSentResp> {
    throw new Error("not implemented")
  }
  async getAppointmentMessages(appointmentId: string): Promise<Message[]> {
    throw new Error("not implemented")
  }
}
