"use client"

import * as React from "react"
import type { ReportMeta, TableElement } from "@/types"
import { TradesTable } from "@/components/TradesTable"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"

function parseDistribution(value?: string) {
  if (!value) return []
  const matches = Array.from(value.matchAll(/([A-Za-z0-9]+):\s*([^\s]+)/g))
  return matches.map((match) => ({ asset: match[1], amount: match[2] }))
}

function mergePortfolioRows(
  startDistribution: Array<{ asset: string; amount: string }>,
  endDistribution: Array<{ asset: string; amount: string }>
) {
  const byAsset = new Map<string, { asset: string; start: string; end: string }>()
  for (const entry of startDistribution) {
    byAsset.set(entry.asset, { asset: entry.asset, start: entry.amount, end: "0" })
  }
  for (const entry of endDistribution) {
    const current = byAsset.get(entry.asset)
    if (current) current.end = entry.amount
    else byAsset.set(entry.asset, { asset: entry.asset, start: "0", end: entry.amount })
  }
  return Array.from(byAsset.values())
}

function splitTables(tables: TableElement[]) {
  const trades = tables.filter((table) => {
    const title = table.title.toLowerCase()
    return title.includes("trade")
  })
  const orders = tables.filter((table) => {
    const title = table.title.toLowerCase()
    return title.includes("order")
  })
  return { trades, orders }
}

function countRows(tables: TableElement[]) {
  return tables.reduce((total, table) => total + table.rows.length, 0)
}

function PortfolioDetails({ meta }: { meta: ReportMeta }) {
  const metrics = meta.summary?.metrics ?? {}
  const startDistribution = parseDistribution(metrics["start portfolio"])
  const endDistribution = parseDistribution(metrics["end portfolio"])
  const rows = mergePortfolioRows(startDistribution, endDistribution)

  if (rows.length === 0) {
    return <div className="py-8 text-center text-sm text-muted-foreground">No portfolio history data.</div>
  }

  return (
    <div className="overflow-hidden rounded-lg border">
      <table className="w-full text-sm">
        <thead className="bg-muted/40">
          <tr>
            <th className="p-3 text-left font-medium text-muted-foreground">Asset</th>
            <th className="p-3 text-left font-medium text-muted-foreground">Start</th>
            <th className="p-3 text-left font-medium text-muted-foreground">End</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.asset} className="border-t border-border/60">
              <td className="p-3 font-medium">{row.asset}</td>
              <td className="p-3 tabular-nums text-foreground/85">{row.start}</td>
              <td className="p-3 tabular-nums">{row.end}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function DataTable({ tables, meta }: { tables: TableElement[]; meta: ReportMeta }) {
  const { trades, orders } = splitTables(tables)
  const tradesCount = countRows(trades)
  const ordersCount = countRows(orders)
  const metrics = meta.summary?.metrics ?? {}
  const portfolioCount = mergePortfolioRows(
    parseDistribution(metrics["start portfolio"]),
    parseDistribution(metrics["end portfolio"])
  ).length
  const defaultTab = trades.length > 0 ? "trades" : orders.length > 0 ? "orders" : "portfolio"
  const [activeTab, setActiveTab] = React.useState(defaultTab)
  React.useEffect(() => {
    setActiveTab(defaultTab)
  }, [defaultTab])

  return (
    <Card className="@container/card mx-4 lg:mx-6">
      <CardHeader className="gap-3">
        <div>
          <CardTitle>Backtesting Details</CardTitle>
          <CardDescription>Trades and orders from the selected run</CardDescription>
        </div>
        <CardAction>
          <ToggleGroup
            type="single"
            value={activeTab}
            onValueChange={(v) => v && setActiveTab(v)}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="trades">
              Trades <Badge variant="secondary">{tradesCount}</Badge>
            </ToggleGroupItem>
            <ToggleGroupItem value="orders">
              Orders <Badge variant="secondary">{ordersCount}</Badge>
            </ToggleGroupItem>
            <ToggleGroupItem value="portfolio">
              Portfolio <Badge variant="secondary">{portfolioCount}</Badge>
            </ToggleGroupItem>
          </ToggleGroup>
          <Select value={activeTab} onValueChange={setActiveTab}>
            <SelectTrigger
              className="flex w-48 @[767px]/card:hidden"
              size="sm"
              aria-label="Select details tab"
            >
              <SelectValue placeholder="Trades" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="trades" className="rounded-lg">Trades</SelectItem>
              <SelectItem value="orders" className="rounded-lg">Orders</SelectItem>
              <SelectItem value="portfolio" className="rounded-lg">Portfolio</SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="pt-0">
        {activeTab === "trades" && <TradesTable elements={trades} />}
        {activeTab === "orders" && <TradesTable elements={orders} />}
        {activeTab === "portfolio" && <PortfolioDetails meta={meta} />}
      </CardContent>
    </Card>
  )
}
