import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react"
import type { ReportMeta } from "@/types"
import { isPositive } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

function toCards(meta: ReportMeta, limit = 4) {
  const metrics = meta.summary?.metrics ?? {}
  const entries = Object.entries(metrics)
  const preferred = [
    "USDT gains",
    "end portfolio USDT value",
    "markets profitability",
    "trades (entries and exits)",
  ]
  const selected = preferred
    .map((key) => [key, metrics[key]] as const)
    .filter(([, value]) => value !== undefined)
  const excluded = new Set([
    ...preferred,
    "start portfolio",
    "end portfolio",
    "start portfolio USDT value",
    "end portfolio USDT value",
  ])
  const fallback = entries.filter(([key]) => !excluded.has(key)).slice(0, Math.max(0, limit - selected.length))
  return [...selected, ...fallback].slice(0, limit)
}

function getCardLabel(title: string) {
  const labels: Record<string, { title: string; detail: string }> = {
    "USDT gains": { title: "Net PnL", detail: "Realized gains in USDT" },
    "end portfolio USDT value": { title: "Final Portfolio Value", detail: "Portfolio total in USDT" },
    "markets profitability": { title: "Market Benchmark", detail: "Underlying market performance" },
    "trades (entries and exits)": { title: "Executed Trades", detail: "Total entries + exits" },
  }
  return labels[title] ?? { title, detail: "Backtesting metric" }
}

export function SectionCards({ meta }: { meta: ReportMeta }) {
  const cards = toCards(meta, 4)
  if (cards.length === 0) return null

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs xl:grid-cols-4 lg:grid-cols-2">
      {cards.map(([title, value]) => {
        const positive = isPositive(value)
        const label = getCardLabel(title)
        return (
          <Card key={title} className="@container/card">
            <CardHeader>
              <CardDescription>{label.detail}</CardDescription>
              <CardTitle className="text-xl font-semibold tabular-nums @[250px]/card:text-2xl">
                {value}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="line-clamp-1 text-xs font-medium">
                {label.title}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
