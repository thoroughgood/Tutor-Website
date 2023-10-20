import { WretchError } from "wretch"

export class HTTPService {
  protected backendURL: string
  protected errorHandlerCallback = async (resp: WretchError) => {
    const error = JSON.parse(resp.message)
    throw new Error(error.error)
  }
  constructor() {
    this.backendURL = "http://127.0.0.1:5000"
  }
}
