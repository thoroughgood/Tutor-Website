import wretch from "wretch"
import { WretchError } from "wretch/resolver"

export interface RegisterBody {
  name: string
  email: string
  password: string
  accountType: "admin" | "tutor" | "student"
}

export interface LoginBody {
  accountType: "admin" | "tutor" | "student"
  email: string
  password: string
}

interface AuthResponse {
  id: string
}

interface AuthService {
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
  async register(registerBody: RegisterBody): Promise<{ id: string }> {
    console.log("register")
    const resp = wretch(`${this.backendURL}/register`)
      .json(registerBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    console.log("fin wrtech")
    return await resp.json()
  }

  async logout(): Promise<{ sucess: boolean }> {
    try {
      const resp = wretch(`${this.backendURL}/logout`).post()
      return await resp.json()
    } catch {
      throw new Error("Failed to log out")
    }
  }
}

export class MockAuthService implements AuthService {
  async login(loginBody: LoginBody) {
    if (
      loginBody.accountType === "student" &&
      loginBody.email === "terrythoroughgood@email.com" &&
      loginBody.password === "goodpassword"
    ) {
      return { id: "35353" }
    }
    throw new Error("something went wrong")
  }
}
