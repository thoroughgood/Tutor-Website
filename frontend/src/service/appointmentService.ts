import { HTTPService } from "./helpers"
import wretch from "wretch"
import { SuccessResponse } from "./types"

export interface Appointment {
  id: string
  startTime: Date
  endTime: Date
  studentId?: string // undefined if no access to appointment
  tutorId: string
  tutorAccepted: boolean
}

interface AppointmentResp extends Omit<Appointment, "startTime" | "endTime"> {
  startTime: string
  endTime: string
}

interface AppointmentsWithTutor {
  yourAppointments: string[]
  other: string[]
}

interface StudentAppointments {
  requested: string[]
  accepted: string[]
  completed: string[]
}

interface AppointmentService {
  requestAppointment: (
    tutorId: string,
    start: Date,
    end: Date,
  ) => Promise<Appointment>
  getTutorAppointments: (tutorId: string) => Promise<AppointmentsWithTutor>
  getAppointment: (appointmentId: string) => Promise<Appointment>
  getOwnStudentAppointments: () => Promise<StudentAppointments>
  acceptAppointment: (appointmentId: string) => Promise<Appointment>
  deleteAppointment: (appointmentId: string) => Promise<SuccessResponse>
  modifyAppointment: (
    appointmentId: string,
    start: Date,
    end: Date,
  ) => Promise<SuccessResponse>
}

export class HTTPAppointmentService
  extends HTTPService
  implements AppointmentService
{
  async requestAppointment(
    tutorId: string,
    start: Date,
    end: Date,
  ): Promise<Appointment> {
    const resp = wretch(`${this.backendURL}/appointment/request`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        tutorId,
        startTime: start.toISOString(),
        endTime: end.toISOString(),
      })
      .post()
    interface RawResp extends Omit<Appointment, "startTime" | "endTime"> {
      startTime: string
      endTime: string
    }
    const respData = (await resp.json()) as RawResp
    return {
      ...respData,
      startTime: new Date(respData.startTime),
      endTime: new Date(respData.endTime),
    }
  }

  async getTutorAppointments(tutorId: string): Promise<AppointmentsWithTutor> {
    const resp = wretch(`${this.backendURL}/tutor/${tutorId}/appointments`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await resp.json()
  }

  async getOwnStudentAppointments(): Promise<StudentAppointments> {
    const resp = wretch(`${this.backendURL}/student/appointments`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    return await resp.json()
  }

  async getAppointment(appointmentId: string): Promise<Appointment> {
    const resp = wretch(`${this.backendURL}/appointment/${appointmentId}`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    const respData = (await resp.json()) as AppointmentResp
    const appointment: Appointment = {
      ...respData,
      startTime: new Date(respData.startTime),
      endTime: new Date(respData.endTime),
    }
    return appointment
  }

  async acceptAppointment(appointmentId: string): Promise<Appointment> {
    const resp = wretch(`${this.backendURL}/appointment/accept`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        id: appointmentId,
        accept: true,
      })
      .put()
    const respData = (await resp.json()) as AppointmentResp
    return {
      ...respData,
      startTime: new Date(respData.startTime),
      endTime: new Date(respData.endTime),
    }
  }

  async deleteAppointment(appointmentId: string): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/appointment/`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        id: appointmentId,
      })
      .delete()
    return await resp.json()
  }

  async modifyAppointment(
    appointmentId: string,
    start: Date,
    end: Date,
  ): Promise<SuccessResponse> {
    const resp = wretch(`${this.backendURL}/appointment/`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .json({
        id: appointmentId,
        startTime: start.toISOString(),
        endTime: end.toISOString(),
      })
      .put()
    return await resp.json()
  }
}

// export class MockAppointmentService implements AppointmentService {
//   private yourAppointments: AppointmentResp[] = []
//   private userId: string
//   constructor(userId: string) {
//     this.userId = userId
//   }
//   private generateMockAppointment(
//     tutorId: string | undefined,
//     startTime: Date | undefined,
//     endTime: Date | undefined,
//   ): AppointmentResp {
//     const newAppointment = {
//       id: nanoid(),
//       startTime: startTime ? startTime : new Date(),
//       endTime: endTime ? endTime : addHours(new Date(), 1),
//       studentId: this.userId,
//       tutorId: tutorId ? tutorId : nanoid(),
//       tutorAccepted: Math.random() > 0.5,
//     }
//     this.yourAppointments.push(newAppointment)
//     return newAppointment
//   }
//   async requestAppointment(tutorId: string, start: Date, end: Date) {
//     return this.generateMockAppointment(tutorId, start, end)
//   }
//
//   async getTutorAppointments(_tutorId: string) {
//     return {
//       yourAppointments: this.yourAppointments,
//       other: this.yourAppointments.map((appointment) => {
//         const other = {
//           ...appointment,
//           startTime: addWeeks(appointment.startTime, 2),
//           endTime: addWeeks(appointment.endTime, 2),
//         }
//         delete other.studentId
//         return other
//       }),
//     }
//   }
// }
