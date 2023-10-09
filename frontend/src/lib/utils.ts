import { type ClassValue, clsx } from "clsx"
import toast from "react-hot-toast"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return prettySentence(error.message)
  if (
    typeof error === "object" &&
    error &&
    "error" in error &&
    typeof error.error === "string"
  ) {
    return prettySentence(error.error)
  }
  return prettySentence(String(error))
}

export function prettySentence(sentence: string): string {
  return sentence.replace(/^./, (c) => c.toUpperCase())
}

export async function toastProtectedFnCall(fn: Function) {
  try {
    await fn()
    return true
  } catch (error) {
    toast.error(getErrorMessage(error))
  }
  return false
}
