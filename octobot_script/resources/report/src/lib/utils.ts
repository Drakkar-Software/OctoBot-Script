import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function isPositive(value: string | number | null | undefined): boolean | null {
  if (value === null || value === undefined) return null
  if (typeof value === "number") return value > 0

  const text = String(value).trim()
  if (!text) return null

  if (text.startsWith("+")) return true
  if (text.startsWith("-")) return false

  const match = text.match(/-?\d+(?:\.\d+)?/)
  if (!match) return null
  const parsed = Number(match[0])
  if (Number.isNaN(parsed)) return null
  return parsed > 0
}
