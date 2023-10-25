interface AppointmentResp {
  id: string
  startTime: string
  endTime: string
  studentId: string
  tutorId: string
  tutorAccepted: boolean
}

interface AppointmentService {
  requestAppointment: () => Promise<AppointmentResp>
}
