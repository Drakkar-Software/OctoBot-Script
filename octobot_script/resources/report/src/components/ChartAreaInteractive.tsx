"use client"

import * as React from "react"
import type { ChartElement } from "@/types"
import { TradingChart } from "@/components/TradingChart"
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

interface ChartGroups {
  all: ChartElement[]
  tradesOrders: ChartElement[]
  indicators: ChartElement[]
  portfolioHistory: ChartElement[]
}

function getTabElements(groups: ChartGroups, tab: string): ChartElement[] {
  if (tab === "trades-orders") return groups.tradesOrders
  if (tab === "indicators") return groups.indicators
  if (tab === "portfolio-history") return groups.portfolioHistory
  return groups.all
}

export function ChartAreaInteractive({
  title,
  description,
  groups,
  height = 320,
}: {
  title: string
  description?: string
  groups: ChartGroups
  height?: number
}) {
  const [activeTab, setActiveTab] = React.useState("all")
  const filteredElements = React.useMemo(() => getTabElements(groups, activeTab), [groups, activeTab])

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
        <CardAction>
          <ToggleGroup
            type="single"
            value={activeTab}
            onValueChange={(v) => v && setActiveTab(v)}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="all">All</ToggleGroupItem>
            <ToggleGroupItem value="trades-orders">Trades &amp; Orders</ToggleGroupItem>
            <ToggleGroupItem value="indicators">Indicators</ToggleGroupItem>
            <ToggleGroupItem value="portfolio-history">Portfolio history</ToggleGroupItem>
          </ToggleGroup>
          <Select value={activeTab} onValueChange={setActiveTab}>
            <SelectTrigger
              className="flex w-40 @[767px]/card:hidden"
              size="sm"
              aria-label="Select chart group"
            >
              <SelectValue placeholder="All" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="all" className="rounded-lg">All</SelectItem>
              <SelectItem value="trades-orders" className="rounded-lg">Trades &amp; Orders</SelectItem>
              <SelectItem value="indicators" className="rounded-lg">Indicators</SelectItem>
              <SelectItem value="portfolio-history" className="rounded-lg">Portfolio history</SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-2 sm:px-6 sm:pt-4">
        {filteredElements.length > 0 ? (
          <TradingChart elements={filteredElements} height={height} />
        ) : (
          <div className="flex min-h-[240px] items-center justify-center text-sm text-muted-foreground">
            No chart available for this tab.
          </div>
        )}
      </CardContent>
    </Card>
  )
}
