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

interface AuthService {
  login: (loginBody: LoginBody) => Promise<AuthResponse>
  register: (registerBody: RegisterBody) => Promise<AuthResponse>
  logout: () => Promise<SuccessResponse>
}

export class HTTPAuthService extends HTTPService implements AuthService {
  async login(loginBody: LoginBody): Promise<AuthResponse> {
    const resp = wretch(`${this.backendURL}/login`)
      .json(loginBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }
  async register(registerBody: RegisterBody): Promise<AuthResponse> {
    const resp = wretch(`${this.backendURL}/register`)
      .json(registerBody)
      .post()
      .notFound(this.errorHandlerCallback)
      .badRequest(this.errorHandlerCallback)
      .error(415, this.errorHandlerCallback)
    return await resp.json()
  }

  async logout(): Promise<SuccessResponse> {
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
  async register(registerBody: RegisterBody) {
    return { id: "1337" }
  }
  async logout() {
    return { success: true }
  }
}
