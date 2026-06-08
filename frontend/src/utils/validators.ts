export function validateCF(cf: string): boolean {
  if (!cf) return true // optional
  const re = /^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$/i
  return re.test(cf.trim())
}

export function validateEmail(email: string): boolean {
  if (!email) return true
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}

export function validateImporto(value: string): boolean {
  const n = parseFloat(value.replace(',', '.'))
  return !isNaN(n) && n > 0
}
