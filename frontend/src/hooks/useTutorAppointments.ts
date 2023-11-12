import {
  Appointment,
  HTTPAppointmentService,
} from "@/service/appointmentService"
import { UseQueryResult, useQueries, useQuery } from "react-query"

const appointmentService = new HTTPAppointmentService()
export default function useTutorAppointments(tutorId: string) {
  const { data: tutorAppointments } = useQuery({
    queryKey: ["tutors", tutorId, "appointments"],
    queryFn: async () => await appointmentService.getTutorAppointments(tutorId),
  })

  const yourAppointmentsQueries = useQueries(
    tutorAppointments?.yourAppointments.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: () => appointmentService.getAppointment(id),
    })) || [],
  )

  const otherAppointmentsQueries = useQueries(
    tutorAppointments?.other.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: () => appointmentService.getAppointment(id),
    })) || [],
  )

  const getAppointmentsFromQueries = (
    queries: UseQueryResult<Appointment>[],
  ) => {
    const appointments = queries
      .filter((query) => query.data !== undefined)
      .map((query) => query.data as Appointment)
    return appointments
  }

  return {
    yourAppointments: getAppointmentsFromQueries(yourAppointmentsQueries),
    other: getAppointmentsFromQueries(otherAppointmentsQueries),
  }
}
