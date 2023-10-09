import SmallProfileCard from "@/components/smallProfileCard"
import { useQuery } from "react-query"

export default function FindTutor() {
  const { data: tutorIds } = useQuery({})
  return (
    <div className="h-full w-full p-16">
      <SmallProfileCard id="1" accountType="tutor" />
    </div>
  )
}
