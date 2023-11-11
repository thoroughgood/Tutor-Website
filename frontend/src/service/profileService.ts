import TutorProfile from "@/pages/tutor/[tutorId]"
import wretch from "wretch"
import { SuccessResponse } from "./types"
import { HTTPService } from "./helpers"

interface UserProfile {
  id: string
  name: string
  bio: string
  email: string
  profilePicture: string | null
  location: string | null
  phoneNumber: string | null
}

export interface TutorProfile extends UserProfile {
  courseOfferings: string[]
  timesAvailable: {
    startTime: string
    endTime: string
  }[]
  documentIds: string[]
}

export interface StudentProfile extends UserProfile {}
export interface TutorSelfEditReqBody extends Omit<TutorProfile, "id"> {}
export interface StudentSelfEditReqBody extends Omit<StudentProfile, "id"> {}

/**
 * ProfileService provides operations relating to tutor/student profiles
 */
export interface TutorSearchParams {
  name?: string
  location?: string
  rating?: string
  courseOfferings?: string[]
  timeRange?: {
    startTime: string
    endTime: string
  }
}

export interface AdminSearchParams {
  name?: string
  phoneNumber?: string
  location?: string
  id?: string
  email?: string
}
export interface ProfileService {
  getTutorProfile: (tutorId: string) => Promise<TutorProfile>
  setOwnTutorProfile: (
    tutorProfile: TutorSelfEditReqBody,
  ) => Promise<SuccessResponse>
  searchTutors: (
    searchParams: TutorSearchParams,
  ) => Promise<{ tutorIds: string[] }>
  searchAll: (searchParams: AdminSearchParams) => Promise<{
    userInfos: { id: string; accountType: "tutor" | "student" | "admin" }[]
  }>
  getStudentProfile: (studentId: string) => Promise<StudentProfile>
  setOwnStudentProfile: (
    studentProfile: StudentSelfEditReqBody,
  ) => Promise<SuccessResponse>
  getUserType: (userId: string) => Promise<"tutor" | "student" | "admin">
  resetPassword: (password: string, id: string) => Promise<SuccessResponse>
}

export class HTTPProfileService extends HTTPService implements ProfileService {
  async searchTutors(
    searchParams: TutorSearchParams,
  ): Promise<{ tutorIds: string[] }> {
    const url = new URL(`${this.backendURL}/searchtutor`)
    const basicParams = { ...searchParams }
    delete basicParams.courseOfferings
    delete basicParams.timeRange
    const params = new URLSearchParams(basicParams as Record<string, string>)
    if (searchParams.timeRange) {
      params.set("timeRange", JSON.stringify(searchParams.timeRange))
    }
    if (searchParams.courseOfferings) {
      params.set(
        "courseOfferings",
        JSON.stringify(searchParams.courseOfferings),
      )
    }
    url.search = params.toString()
    const data = wretch(url.toString()).get()
    return await data.json()
  }

  async searchAll(searchParams: AdminSearchParams): Promise<{
    userInfos: { id: string; accountType: "tutor" | "student" | "admin" }[]
  }> {
    const url = new URL(`${this.backendURL}/admin/search`)
    const basicParams = { ...searchParams }
    const params = new URLSearchParams(basicParams as Record<string, string>)

    url.search = params.toString()
    const data = wretch(url.toString())
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await data.json()
  }

  async getDocument(docId: string): Promise<{ document: string }> {
    const data = wretch(`${this.backendURL}/document/${docId}`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await data.json()
  }

  async uploadDocument(documents: string): Promise<{ id: string }> {
    const data = wretch(`${this.backendURL}/document`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({ document: documents })
      .post()
    return await data.json()
  }

  async getTutorProfile(tutorId: string): Promise<TutorProfile> {
    const resp = wretch(`${this.backendURL}/tutor/${tutorId}`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await resp.json()
  }

  async setOwnTutorProfile(
    tutorProfile: TutorSelfEditReqBody,
  ): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/tutor/profile`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json(tutorProfile)
      .put()
    return resp.json()
  }

  async deleteOwnTutorProfile(): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/tutor/`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({})
      .delete()
    return await resp.json()
  }

  async getStudentProfile(studentId: string): Promise<StudentProfile> {
    const resp = wretch(`${this.backendURL}/student/${studentId}`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await resp.json()
  }

  async setOwnStudentProfile(
    studentProfile: StudentSelfEditReqBody,
  ): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/student/profile`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json(studentProfile)
      .put()
    return resp.json()
  }
  async deleteOwnStudentProfile(): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/student/`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({})
      .delete()
    return await resp.json()
  }

  async getUserType(userId: string): Promise<"tutor" | "student" | "admin"> {
    const resp = wretch(`${this.backendURL}/utils/usertype/${userId}`).get()
    const respData = (await resp.json()) as {
      accountType: "tutor" | "student" | "admin"
    }
    return respData.accountType
  }

  async resetPassword(
    password: string,
    profileId: string,
  ): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/resetpassword`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({ newPassword: password, id: profileId })
      .put()
    return await resp.json()
  }

  async adminDeleteProfile(
    profileId: string,
    accountType: string,
  ): Promise<SuccessResponse> {
    if (accountType === "student") {
      const resp = wretch(`${this.backendURL}/student/`)
        .options({
          credentials: "include",
          mode: "cors",
        })
        .json({ id: profileId })
        .delete()
      return await resp.json()
    } else if (accountType === "tutor") {
      const resp = wretch(`${this.backendURL}/tutor/`)
        .options({
          credentials: "include",
          mode: "cors",
        })
        .json({ id: profileId })
        .delete()
      return await resp.json()
    }
    return { success: false }
  }
}

export class MockProfileService implements ProfileService {
  private mockTutorProfile: TutorProfile = {
    id: "1337",
    name: "Daniel Nguyen",
    bio: "I tutor Computer Science at UNSW and I like grape gummy candy. It is a pleasure to meet you.",
    email: "daniel.nguyen.s173@gmail.com",
    profilePicture: null,
    location: "Sydney",
    phoneNumber: "0411111111",
    courseOfferings: ["COMP2041", "COMP6080"],
    timesAvailable: [
      // {
      //   startTime: addHours(new Date(), 24).toISOString(),
      //   endTime: addHours(new Date(), 25).toISOString(),
      // },
      // {
      //   startTime: addHours(new Date(), 48).toISOString(),
      //   endTime: addHours(new Date(), 54).toISOString(),
      // },
      // {
      //   startTime: addHours(new Date(), 32).toISOString(),
      //   endTime: addHours(new Date(), 38).toISOString(),
      // },
    ],
    documentIds: [],
  }

  private mockStudentProfile: StudentProfile = {
    id: "64",
    name: "Daniel Wang",
    bio: "I need help with COMP6080",
    email: "daniel.wang@gmail.com",
    profilePicture: null,
    location: "Sydney",
    phoneNumber: "0499999999",
  }
  async getTutorProfile(_tutorId: string) {
    return this.mockTutorProfile
  }

  async searchAll(_searchParams: AdminSearchParams) {
    return { userInfos: [{ id: "1337", accountType: "tutor" as "tutor" }] }
  }

  async resetPassword(_profileId: string) {
    return { success: true }
  }

  async setOwnTutorProfile(tutorProfile: TutorSelfEditReqBody) {
    this.mockTutorProfile = { ...tutorProfile, id: "1337" }
    return { success: true }
  }

  async deleteOwnTutorProfile(_tutorId: string) {
    return { success: true }
  }

  async searchTutors(_searchParams: TutorSearchParams) {
    return { tutorIds: ["1337"] }
  }

  async getStudentProfile(_studentId: string) {
    return this.mockStudentProfile
  }

  async setOwnStudentProfile(studentProfile: StudentSelfEditReqBody) {
    this.mockStudentProfile = {
      ...studentProfile,
      id: this.mockStudentProfile.id,
    }
    return { success: true }
  }

  async getUserType(_userId: string): Promise<"tutor" | "student" | "admin"> {
    return "tutor"
  }
}
