import { HTTPAppointmentService } from "@/service/appointmentService"
import { useQuery } from "react-query"

const appointmentService = new HTTPAppointmentService()
export default function useAppointmentQuery(id: string) {
  const query = useQuery({
    queryFn: async () => appointmentService.getAppointment(id),
    queryKey: ["appointments", id],
  })
  return query
}
