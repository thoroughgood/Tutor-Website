import { HTTPService } from "./helpers"
import wretch from "wretch"

interface Appointment {
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
  yourAppointments: Appointment[]
  other: Appointment[]
}

interface StudentAppointmentsResp {
  requested: string[]
  accepted: string[]
  completed: string[]
}

interface StudentAppointments {
  requested: Appointment[]
  accepted: Appointment[]
  completed: Appointment[]
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
    interface RawResp {
      yourAppointments: string[]
      other: string[]
    }
    const respData = (await resp.json()) as RawResp
    const yourAppointmentsPromises = respData.yourAppointments.map((id) =>
      this.getAppointment(id),
    )
    const otherPromises = respData.other.map((id) => this.getAppointment(id))
    const populatedResponse: AppointmentsWithTutor = {
      yourAppointments: await Promise.all(yourAppointmentsPromises),
      other: await Promise.all(otherPromises),
    }
    console.log(populatedResponse)
    return populatedResponse
  }

  async getOwnStudentAppointments(): Promise<StudentAppointments> {
    const resp = wretch(`${this.backendURL}/student/appointments`)
      .options({
        credentials: "include",
        mode: "cors",
      })
      .get()
    const respData = (await resp.json()) as StudentAppointmentsResp
    const populatedResponse: StudentAppointments = {
      requested: await Promise.all(
        respData.requested.map((id) => this.getAppointment(id)),
      ),
      accepted: await Promise.all(
        respData.requested.map((id) => this.getAppointment(id)),
      ),
      completed: await Promise.all(
        respData.requested.map((id) => this.getAppointment(id)),
      ),
    }
    return populatedResponse
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
