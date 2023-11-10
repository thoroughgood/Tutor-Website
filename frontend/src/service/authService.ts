import wretch from "wretch"
import { SuccessResponse } from "./types"
import { HTTPService } from "./helpers"

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

interface CheckUserResponse {
  id: string
  accountType: "tutor" | "admin" | "student"
}

interface AuthService {
  login: (loginBody: LoginBody) => Promise<AuthResponse>
  register: (registerBody: RegisterBody) => Promise<AuthResponse>
  logout: () => Promise<SuccessResponse>
  checkUser: () => Promise<CheckUserResponse>
}

export class HTTPAuthService extends HTTPService implements AuthService {
  async login(loginBody: LoginBody): Promise<AuthResponse> {
    const resp = wretch(`${this.backendURL}/login`)
      // .headers({
      //   "Access-Control-Allow-Credentials": "true",
      // }) // i commented this because i tink its supposed to be from a backend response - daniel n
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json(loginBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)

    return await resp.json()
  }
  async register(registerBody: RegisterBody): Promise<AuthResponse> {
    const resp = wretch(`${this.backendURL}/register`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json(registerBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }

  async logout(): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/logout`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }

  async adminCreate(registerBody: RegisterBody): Promise<AuthResponse> {
    const resp = wretch(`${this.backendURL}/admin/create`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json(registerBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }

  async checkUser(): Promise<CheckUserResponse> {
    try {
      const resp = wretch(`${this.backendURL}/utils/getuserid`)
        .options({
          credentials: "include",
          mode: "cors",
        })
        .get()
      return await resp.json()
    } catch {
      throw new Error("Failed to get user details")
    }
  }
}

export class MockAuthService implements AuthService {
  async login(loginBody: LoginBody) {
    if (
      loginBody.accountType === "tutor" &&
      loginBody.email === "terrythoroughgood@email.com" &&
      loginBody.password === "goodpassword"
    ) {
      return { id: "35353" }
    }
    throw new Error("something went wrong")
  }
  async register(registerBody: RegisterBody) {
    return { id: "1337" }
  }
  async logout() {
    return { success: true }
  }
  async checkUser(): Promise<CheckUserResponse> {
    return { id: "1337", accountType: "tutor" }
  }
}
