import { WretchError } from "wretch"

export class HTTPService {
  protected backendURL: string
  protected errorHandlerCallback = async (resp: WretchError) => {
    const error = JSON.parse(resp.message)
    throw new Error(error.error)
  }
  constructor() {
    this.backendURL = "http://127.0.0.1:8000"
  }
}

export function fileToDataUrl(file: File) {
  const validFileTypes = ["image/jpeg", "image/png", "image/jpg"]
  const valid = validFileTypes.find((type) => type === file.type)
  // Bad data, let's walk away.
  if (!valid) {
    throw Error("provided file is not a png, jpg or jpeg image.")
  }

  const reader = new FileReader()
  const dataUrlPromise = new Promise((resolve, reject) => {
    reader.onerror = reject
    reader.onload = () => resolve(reader.result)
  })
  reader.readAsDataURL(file)
  return dataUrlPromise
}
