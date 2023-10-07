import wretch from "wretch"
import { WretchError } from "wretch/resolver"

export interface RegisterBody {
  name: string
  email: string
  password: string
  accountType: "admin" | "tutor" | "student"
}

export interface LoginBody {
  email: string
  password: string
}

interface AuthResponse {
  id: string
}

interface MockAuthService {
  register: (RegisterBody: RegisterBody) => Promise<AuthResponse>
  login: (LoginBody: LoginBody) => Promise<AuthResponse>
}

export class HTTPAuthService {
  private backendURL: string
  private errorHandlerCallback = async (resp: WretchError) => {
    const error = JSON.parse(resp.message)
    throw new Error(error.error)
  }
  constructor() {
    this.backendURL = process.env.BACKEND_URL || "http://127.0.0.1:5000"
  }
  async register(registerBody: RegisterBody) {
    const resp = wretch(`${this.backendURL}/register`)
      .json(registerBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }

  async login(loginBody: LoginBody) {
    if (
      loginBody.email === "terrythoroughgood@email.com" &&
      loginBody.password === "goodpassword"
    ) {
      return { id: 5363592 }
    }
    throw new Error("something went wrong")
  }
}
