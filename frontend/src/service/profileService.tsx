import TutorProfile from "@/pages/tutor/[tutorId]"
import { SuccessResponse } from "./types"

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
  timeAvailable: {
    startTime: string
    endTime: string
  }[]
}

export interface StudentProfile extends UserProfile {}
export interface TutorSelfEditReqBody extends Omit<TutorProfile, "id"> {}
export interface StudentSelfEditReqBody extends Omit<StudentProfile, "id"> {}

/**
 * ProfileService provides operations relating to tutor/student profiles
 */
interface TutorSearchParams {
  location?: string
  rating?: string
  courseOfferings?: string[]
  timeRange?: {
    startTime: string
    endTime: string
  }
}
export interface ProfileService {
  getTutorProfile: (tutorId: string) => Promise<TutorProfile>
  setOwnTutorProfile: (
    tutorProfile: TutorSelfEditReqBody,
  ) => Promise<SuccessResponse>
  searchTutors: (
    searchParams: TutorSearchParams,
  ) => Promise<{ tutorIds: string[] }>
  getStudentProfile: (studentId: string) => Promise<StudentProfile>
  setOwnStudentProfile: (
    studentProfile: StudentSelfEditReqBody,
  ) => Promise<SuccessResponse>
  searchTutors: (
    searchParams: TutorSearchParams,
  ) => Promise<{ tutorIds: string[] }>
}

// export class HTTPProfileService extends HTTPService implements ProfileService {
//   async searchTutors(searchParams): Promise<{ tutorIds: string[] }> {
//     const url = new URL(`${this.backendURL}/searchtutor`)
//     const params = new URLSearchParams(searchParams)
//     url.search = params.toString()
//     console.log(url)
//     const data = wretch(`${this.backendURL}/searchtutor`).get()
//     return await data.json()
//   }
// }

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
    timeAvailable: [
      {
        startTime: "2023-10-08T12:51:28+11:00",
        endTime: "2023-10-08T13:51:28+11:00",
      },
      {
        startTime: "2023-10-09T12:00:28+11:00",
        endTime: "2023-10-09T15:00:28+11:00",
      },
      {
        startTime: "2023-10-09T17:00:28+11:00",
        endTime: "2023-10-09T20:00:28+11:00",
      },
      {
        startTime: "2023-10-11T17:00:28+11:00",
        endTime: "2023-10-11T20:00:28+11:00",
      },
    ],
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
  async getTutorProfile(tutorId: string) {
    return this.mockTutorProfile
  }

  async setOwnTutorProfile(tutorProfile: TutorSelfEditReqBody) {
    this.mockTutorProfile = { ...tutorProfile, id: this.mockTutorProfile.id }
    console.log(tutorProfile)
    return { success: true }
  }

  async searchTutors(searchParams: TutorSearchParams) {
    return { tutorIds: ["1337"] }
  }

  async getStudentProfile(studentId: string) {
    return this.mockStudentProfile
  }

  async setOwnStudentProfile(studentProfile: StudentSelfEditReqBody) {
    this.mockStudentProfile = {
      ...studentProfile,
      id: this.mockStudentProfile.id,
    }
    return { success: true }
  }

  async deleteOwnUserProfile(userId: string) {
    if (userId === "64" || userId === "1337") {
      return { success: true }
    } else {
      return { success: false }
    }
  }
}
