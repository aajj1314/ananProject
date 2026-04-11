/**
 * 将ISO时间字符串格式化为相对时间描述
 * @param isoString - ISO 8601格式的时间字符串
 * @returns 格式化后的相对时间字符串，如"刚刚"、"5分钟前"、"2小时前"等
 */
export function formatRelativeTime(isoString: string): string {
  if (!isoString) return '暂无数据'
  const now = Date.now()
  const target = new Date(isoString).getTime()
  if (isNaN(target)) return isoString
  const diff = now - target
  if (diff < 60_000) return '刚刚'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}分钟前`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}小时前`
  if (diff < 604_800_000) return `${Math.floor(diff / 86_400_000)}天前`
  const d = new Date(isoString)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
