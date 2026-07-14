export function formatDate(value: string | null, options?: Intl.DateTimeFormatOptions) {
  if (!value) return "Not available";
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  if (Number.isNaN(date.getTime())) return "Not available";
  return new Intl.DateTimeFormat(undefined, options ?? { dateStyle: "medium" }).format(date);
}
export function formatDateTime(value: string | null) { return formatDate(value, { dateStyle: "medium", timeStyle: "short" }); }
