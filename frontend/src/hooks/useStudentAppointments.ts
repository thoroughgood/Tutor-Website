import { UseQueryResult, useQueries, useQuery } from "react-query"
import useUser from "./useUser"
import {
  Appointment,
  HTTPAppointmentService,
} from "@/service/appointmentService"

const appointmentService = new HTTPAppointmentService()
export default function useStudentAppointments() {
  const { user } = useUser()
  const { data: studentAppointmentIds } = useQuery({
    queryKey: ["student", user?.userId, "appointments"],
    queryFn: () => appointmentService.getOwnStudentAppointments(),
  })

  const requestedAppointmentsQueries = useQueries(
    studentAppointmentIds?.requested.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )
  const acceptedAppointmentQueries = useQueries(
    studentAppointmentIds?.accepted.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
    })) || [],
  )
  const completedAppointmentQueries = useQueries(
    studentAppointmentIds?.completed.map((id) => ({
      queryKey: ["appointments", id],
      queryFn: async () => appointmentService.getAppointment(id),
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
    requested: getAppointmentsFromQueries(requestedAppointmentsQueries),
    accepted: getAppointmentsFromQueries(acceptedAppointmentQueries),
    completed: getAppointmentsFromQueries(completedAppointmentQueries),
  }
}
