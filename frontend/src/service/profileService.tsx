import TutorProfile from "@/pages/tutor/[tutorId]"
import { SuccessResponse } from "./types"

export interface TutorProfile {
  id: string
  name: string
  bio: string
  email: string
  profilePicture: string | null
  location: string | null
  phoneNumber: string | null
  courseOfferings: string[]
  timeAvailable: {
    startTime: string
    endTime: string
  }[]
}

/**
 * ProfileService provides operations relating to tutor/student profiles
 */
export interface ProfileService {
  getTutorProfile: (tutorId: string) => Promise<TutorProfile>
  setTutorProfile: (
    tutorId: string,
    tutorProfile: TutorProfile,
  ) => Promise<SuccessResponse>
}

export class MockProfileService implements ProfileService {
  private mockProfile: TutorProfile = {
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
  async getTutorProfile(tutorId: string) {
    return this.mockProfile
  }

  async setTutorProfile(tutoriId: string, tutorProfile: TutorProfile) {
    this.mockProfile = tutorProfile
    return { success: true }
  }
}
