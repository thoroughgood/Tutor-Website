import { type ClassValue, clsx } from "clsx"
import { areIntervalsOverlapping, max } from "date-fns"
import toast from "react-hot-toast"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    error = error.message
  }
  if (typeof error === "string") {
    try {
      error = JSON.parse(error)
    } catch {}
  }
  if (
    typeof error === "object" &&
    error &&
    "error" in error &&
    typeof error.error === "string"
  ) {
    try {
      return prettySentence(JSON.parse(error.error))
    } catch {}
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
    console.error(error)
    toast.error(getErrorMessage(error))
  }
  return false
}

export function getMergedIntervals(intervals: Interval[]) {
  if (intervals.length == 0) return [...intervals]
  const sorted = [...intervals].sort(
    (aInter, bInter) => aInter.start.valueOf() - bInter.start.valueOf(),
  )
  const merged = [sorted[0]]
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i].start <= merged[merged.length - 1].end) {
      merged[merged.length - 1].end = max([
        merged[merged.length - 1].end,
        sorted[i].end,
      ])
    } else {
      merged.push(sorted[i])
    }
  }
  return merged
}

export function excludeInterval(intervals: Interval[], toExclude: Interval) {
  const result: Interval[] = []
  for (let i = 0; i < intervals.length; i++) {
    if (!areIntervalsOverlapping(intervals[i], toExclude)) {
      result.push({ ...intervals[i] })
      continue
    }
    if (
      toExclude.start > intervals[i].start &&
      toExclude.end < intervals[i].end
    ) {
      // case 1: inside
      const leftInterval = {
        start: intervals[i].start,
        end: toExclude.start,
      }
      const rightInterval = {
        start: toExclude.end,
        end: intervals[i].end,
      }
      result.push(leftInterval)
      result.push(rightInterval)
    } else if (
      toExclude.start <= intervals[i].start &&
      toExclude.end < intervals[i].end
    ) {
      // case 2: only overlaps left edge
      result.push({ start: toExclude.end, end: intervals[i].end })
    } else if (
      toExclude.end >= intervals[i].end &&
      toExclude.start > intervals[i].start
    ) {
      // case 3: only overlaps right edge
      result.push({ start: intervals[i].start, end: toExclude.start })
    }
    // case 4: exlusion covers entire interval, don't append
  }
  return result
}
