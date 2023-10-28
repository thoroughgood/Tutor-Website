import IconInput from "@/components/iconInput"
import SmallProfileCard from "@/components/smallProfileCard"

import { HTTPProfileService } from "@/service/profileService"
import { Loader2, Phone, User, Mail } from "lucide-react"
import { useMemo, useState } from "react"
import { useQuery } from "react-query"
import { useDebounce } from "usehooks-ts"

const profileService = new HTTPProfileService()

export default function FindUser() {
  const [name, setName] = useState<string>("")
  const [phoneNumber, setPhoneNumber] = useState<string>("")
  const [userId, setUserId] = useState<string>("")
  const [email, setEmail] = useState<string>("")
  const [accountType, setAccountType] = useState<string>("")
  const [filterText, setFilterText] = useState("")
  const [filterOpen, setFilterOpen] = useState(false)

  const searchParams = useMemo(() => {
    // Build the param obj from all the fields
    // Deletes key if 'null' since we want to use whitelist filtering
    const allParams = {
      id: userId === "" ? null : userId,
      name: name === "" ? null : name,
      email: email === "" ? null : email,
      phoneNumber: phoneNumber === "" ? null : phoneNumber,
      accountType: accountType === "" ? null : accountType,
    }
    return Object.fromEntries(
      Object.entries(allParams).filter(([k, v]) => v !== null),
    )
  }, [name, phoneNumber, userId, email, accountType])

  const debouncedSearchParams = useDebounce(searchParams, 250)

  const { data: searchResp, isLoading } = useQuery({
    queryKey: ["userList", debouncedSearchParams],
    queryFn: async () => {
      return await profileService.searchAll(debouncedSearchParams)
    },
  })

  //gonna need to sort through the searchResp and somehow map account types and ids together

  return (
    <div className="flex h-full w-full flex-col justify-center gap-10 p-16 md:justify-start">
      {/* Basic Inputs */}
      <div className="flex flex-col gap-2 rounded-md bg-secondary p-5 shadow-md">
        <h1 className="text-2xl text-secondary-foreground">
          Search For A User
        </h1>
        <div className="flex w-full flex-col gap-2 md:flex-row">
          <IconInput
            onChange={(e) => setName(e.currentTarget.value)}
            placeholder="Name"
          >
            <User className="h-5 w-5" />
          </IconInput>
          <IconInput
            onChange={(e) => setPhoneNumber(e.currentTarget.value)}
            placeholder="Phone Number"
          >
            <Phone className="h-5 w-5" />
          </IconInput>
          <IconInput
            onChange={(e) => setUserId(e.currentTarget.value)}
            placeholder="ID"
          >
            <User className="h-5 w-5" />
          </IconInput>
          <IconInput
            onChange={(e) => setEmail(e.currentTarget.value)}
            placeholder="Email"
          >
            <Mail className="h-5 w-5" />
          </IconInput>
        </div>
      </div>
      {/* Tutor search results */}
      <div className="flex flex-wrap justify-center gap-5">
        {isLoading ? (
          <Loader2 className="animate-spin" />
        ) : (
          searchResp?.userInfos.map((tId) => (
            <SmallProfileCard
              key={tId.id}
              id={tId.id}
              accountType={tId.accountType}
            />
          ))
        )}
      </div>
    </div>
  )
}
