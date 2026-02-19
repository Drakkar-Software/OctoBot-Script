import type { ValueElement } from "@/types"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { isPositive } from "@/lib/utils"
import {
  Activity,
  AlertTriangle,
  BarChart2,
  DollarSign,
  Percent,
  TrendingDown,
  TrendingUp,
} from "lucide-react"
import { cn } from "@/lib/utils"

const METRIC_ICONS: Record<string, React.ReactNode> = {
  roi: <Percent className="size-4" />,
  gain: <TrendingUp className="size-4" />,
  gains: <TrendingUp className="size-4" />,
  return: <TrendingUp className="size-4" />,
  "win rate": <Activity className="size-4" />,
  wins: <BarChart2 className="size-4" />,
  losses: <TrendingDown className="size-4" />,
  trades: <BarChart2 className="size-4" />,
  drawdown: <AlertTriangle className="size-4" />,
  portfolio: <DollarSign className="size-4" />,
  profit: <TrendingUp className="size-4" />,
}

function getIcon(title: string): React.ReactNode {
  const key = title.toLowerCase()
  for (const [match, icon] of Object.entries(METRIC_ICONS)) {
    if (key.includes(match)) return icon
  }
  return <BarChart2 className="size-4" />
}

function getValueColor(title: string, value: string | null): string {
  const titleLower = title.toLowerCase()
  const pos = isPositive(value)
  if (pos === null) return "text-foreground"
  const negativeGoodMetrics = ["drawdown", "loss", "losses"]
  const isNegativeGood = negativeGoodMetrics.some((m) => titleLower.includes(m))
  if (isNegativeGood) return pos ? "text-destructive" : "text-foreground"
  return pos ? "text-foreground" : "text-destructive"
}

interface MetricCardProps {
  title: string
  value: string | null
}

function MetricCard({ title, value }: MetricCardProps) {
  const icon = getIcon(title)
  const valueColor = getValueColor(title, value)

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="cursor-default rounded-xl border border-border bg-card px-4 py-4 flex items-start justify-between gap-3 hover:bg-card/80 transition-colors">
          <div className="flex flex-col gap-1 min-w-0 flex-1">
            <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider truncate leading-none">
              {title}
            </p>
            <p className={cn("text-lg font-semibold tabular-nums leading-tight mt-1", valueColor)}>
              {value ?? "—"}
            </p>
          </div>
          <div className="flex items-center justify-center size-8 rounded-lg bg-muted/60 text-muted-foreground shrink-0">
            {icon}
          </div>
        </div>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <p>{title}</p>
      </TooltipContent>
    </Tooltip>
  )
}

interface MetricCardsProps {
  elements: ValueElement[]
}

interface GroupedMetric {
  baseTitle: string
  start?: string | null
  end?: string | null
}

function normalizeTitle(title: string): string {
  return title.trim().replace(/\s+/g, " ")
}

function groupMetrics(elements: Array<{ title: string; value: string | null }>) {
  const grouped = new Map<string, GroupedMetric>()
  const singles: Array<{ title: string; value: string | null }> = []

  for (const element of elements) {
    const normalizedTitle = normalizeTitle(element.title)
    const lower = normalizedTitle.toLowerCase()
    if (lower.startsWith("start ")) {
      const baseTitle = normalizedTitle.slice(6)
      const key = baseTitle.toLowerCase()
      const current = grouped.get(key) ?? { baseTitle }
      current.start = element.value
      grouped.set(key, current)
      continue
    }
    if (lower.startsWith("end ")) {
      const baseTitle = normalizedTitle.slice(4)
      const key = baseTitle.toLowerCase()
      const current = grouped.get(key) ?? { baseTitle }
      current.end = element.value
      grouped.set(key, current)
      continue
    }
    singles.push(element)
  }

  return {
    groups: Array.from(grouped.values()),
    singles,
  }
}

function GroupMetricCard({ baseTitle, start, end }: GroupedMetric) {
  const title = normalizeTitle(baseTitle)
  const valueColor = getValueColor(title, end ?? start ?? null)
  return (
    <div className="cursor-default rounded-xl border border-border bg-card px-4 py-4 flex flex-col gap-2 hover:bg-card/80 transition-colors">
      <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider truncate leading-none">
        {title}
      </p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Start</p>
          <p className="text-sm font-medium tabular-nums text-foreground mt-1">{start ?? "—"}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">End</p>
          <p className={cn("text-sm font-medium tabular-nums mt-1", valueColor)}>{end ?? "—"}</p>
        </div>
      </div>
    </div>
  )
}

export function MetricCards({ elements }: MetricCardsProps) {
  const displayable = elements.filter((el) => el.html === null && el.title !== null && el.value !== null)
  if (displayable.length === 0) return null

  const parsed = displayable.map((element) => ({ title: element.title!, value: element.value }))
  const { groups, singles } = groupMetrics(parsed)
  const cardCount = groups.length + singles.length

  return (
    <div
      className={cn(
        "grid gap-3",
        cardCount <= 3
          ? "grid-cols-1 sm:grid-cols-3"
          : cardCount <= 4
            ? "grid-cols-2 sm:grid-cols-4"
            : cardCount <= 6
              ? "grid-cols-2 sm:grid-cols-3 xl:grid-cols-6"
              : "grid-cols-2 sm:grid-cols-3 xl:grid-cols-4"
      )}
    >
      {groups.map((group) => (
        <GroupMetricCard
          key={group.baseTitle}
          baseTitle={group.baseTitle}
          start={group.start}
          end={group.end}
        />
      ))}
      {singles.map((el) => (
        <MetricCard key={el.title} title={el.title} value={el.value} />
      ))}
    </div>
  )
}

interface HtmlMetricProps {
  elements: ValueElement[]
}

export function HtmlMetrics({ elements }: HtmlMetricProps) {
  const htmlElements = elements.filter((el) => el.html !== null)
  if (htmlElements.length === 0) return null

  return (
    <div className="mt-4 grid gap-3 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
      {htmlElements.map((el, i) => (
        <div key={i} className="rounded-xl border border-border bg-card overflow-hidden">
          {el.title && (
            <div className="px-4 py-2.5 border-b border-border">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {el.title}
              </p>
            </div>
          )}
          {/* biome-ignore lint/security/noDangerouslySetInnerHtml: report HTML from trusted Python backend */}
          <div
            className="octobot-metric-html px-4 py-3"
            dangerouslySetInnerHTML={{ __html: el.html! }}
          />
        </div>
      ))}
    </div>
  )
}
