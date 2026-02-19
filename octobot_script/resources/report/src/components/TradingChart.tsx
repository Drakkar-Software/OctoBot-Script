"use client"

import type { ChartElement } from "@/types"
import { useEffect, useRef } from "react"
import { cn } from "@/lib/utils"
import {
  ColorType,
  createChart,
  LineStyle,
  PriceScaleMode,
  type UTCTimestamp,
} from "lightweight-charts"

const THEME = {
  bg: "#071633",
  grid: "#2a2e39",
  text: "#b2b5be",
}

const CANDLE_COLORS = {
  up: "#18b07a",
  down: "#f6465d",
}

interface LegendItem {
  key: string
  label: string
  color: string
}

interface MarkerPoint {
  time: UTCTimestamp
  position: "aboveBar" | "belowBar"
  color: string
  shape: "arrowUp" | "arrowDown" | "circle"
  text: string
}

interface AppliedElement {
  series: any | null
  markers: MarkerPoint[]
  isCandles: boolean
  timeSet: Set<number>
}

function toTime(raw: number | string): UTCTimestamp | null {
  if (typeof raw === "number") {
    if (raw > 10_000_000_000) return Math.floor(raw / 1000) as UTCTimestamp
    return Math.floor(raw) as UTCTimestamp
  }
  const parsed = Date.parse(raw)
  if (Number.isNaN(parsed)) return null
  return Math.floor(parsed / 1000) as UTCTimestamp
}

function isIndicatorElement(el: ChartElement): boolean {
  return /\b(rsi|signals?|macd|stoch|indicator)\b/i.test(el.title)
}

function inferIsLogScale(elements: ChartElement[]): boolean {
  if (!elements.some((el) => el.y_type === "log")) return false
  for (const el of elements) {
    const series = [el.y, el.open, el.high, el.low, el.close]
    for (const arr of series) {
      if (!Array.isArray(arr)) continue
      for (const v of arr) {
        if (typeof v !== "number" || !Number.isFinite(v) || v <= 0) return false
      }
    }
  }
  return true
}

function getColorAt(el: ChartElement, index = 0, fallback = "#7dd3fc"): string {
  if (typeof el.color === "string") return el.color
  if (Array.isArray(el.color) && typeof el.color[index] === "string") return el.color[index] as string
  return fallback
}

function getSeriesLineColor(el: ChartElement, fallback = "#a78bfa"): string {
  return getColorAt(el, 0, fallback)
}

function isValidNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value)
}

function toLineData(el: ChartElement) {
  if (!el.x || !el.y) return []
  const size = Math.min(el.x.length, el.y.length)
  const data: Array<{ time: UTCTimestamp; value: number }> = []
  for (let i = 0; i < size; i += 1) {
    const time = toTime(el.x[i] as number | string)
    const value = el.y[i]
    if (time === null || !isValidNumber(value)) continue
    data.push({ time, value })
  }
  data.sort((a, b) => a.time - b.time)
  const deduped: Array<{ time: UTCTimestamp; value: number }> = []
  for (const point of data) {
    if (deduped.length > 0 && deduped[deduped.length - 1].time === point.time) {
      deduped[deduped.length - 1] = point
    } else {
      deduped.push(point)
    }
  }
  return deduped
}

function toCandleData(el: ChartElement) {
  if (!el.x || !el.open || !el.high || !el.low || !el.close) return []
  const size = Math.min(el.x.length, el.open.length, el.high.length, el.low.length, el.close.length)
  const data: Array<{ time: UTCTimestamp; open: number; high: number; low: number; close: number }> = []
  for (let i = 0; i < size; i += 1) {
    const time = toTime(el.x[i] as number | string)
    const open = el.open[i]
    const high = el.high[i]
    const low = el.low[i]
    const close = el.close[i]
    if (
      time === null ||
      !isValidNumber(open) ||
      !isValidNumber(high) ||
      !isValidNumber(low) ||
      !isValidNumber(close)
    ) continue
    data.push({ time, open, high, low, close })
  }
  data.sort((a, b) => a.time - b.time)
  const deduped: Array<{ time: UTCTimestamp; open: number; high: number; low: number; close: number }> = []
  for (const point of data) {
    if (deduped.length > 0 && deduped[deduped.length - 1].time === point.time) {
      deduped[deduped.length - 1] = point
    } else {
      deduped.push(point)
    }
  }
  return deduped
}

function buildMarkers(el: ChartElement) {
  if (!el.x) return []
  const markers: MarkerPoint[] = []
  for (let i = 0; i < el.x.length; i += 1) {
    const time = toTime(el.x[i] as number | string)
    if (time === null) continue
    const text = Array.isArray(el.text) ? String(el.text[i] ?? "") : ""
    const lower = text.toLowerCase()
    const isBuy = lower.includes("buy") || lower.includes("long")
    const isStopLoss = lower.includes("stop_loss") || lower.includes("stop loss")
    const isLimitSell = lower.includes("limit") && lower.includes("sell")
    const isSell = lower.includes("sell") || lower.includes("short") || isStopLoss
    const color = isBuy
      ? "#22c55e"
      : isStopLoss
        ? "#ef4444"
        : isLimitSell
          ? "#f59e0b"
          : isSell
            ? "#f43f5e"
            : getColorAt(el, i, "#38bdf8")
    const shape = isBuy ? "arrowUp" : isSell ? "arrowDown" : "circle"
    const position = isBuy ? "belowBar" : "aboveBar"
    const label = isBuy
      ? "BUY"
      : isStopLoss
        ? "SL"
        : isLimitSell
          ? "TP"
          : isSell
            ? "SELL"
            : ""
    markers.push({
      time,
      position,
      color,
      shape,
      text: label,
    })
  }
  return markers
}

function filterMarkersByTimes(markers: MarkerPoint[], times: Set<number>) {
  if (times.size === 0) return []
  return markers.filter((m) => times.has(m.time))
}

function isMarkerElement(el: ChartElement): boolean {
  return (el.mode ?? "").includes("markers")
}

function getLegendItems(elements: ChartElement[]): LegendItem[] {
  return elements
    .filter((el) => !el.is_hidden && el.x !== null && el.title !== "candles_source")
    .map((el) => ({
      key: el.title,
      label: el.title.replaceAll("_", " ").toLowerCase(),
      color: el.kind === "candlestick" ? CANDLE_COLORS.up : getSeriesLineColor(el),
    }))
}

function buildChart(container: HTMLDivElement, height: number, isLogScale: boolean) {
  return createChart(container, {
    height,
    layout: {
      background: { type: ColorType.Solid, color: THEME.bg },
      textColor: THEME.text,
    },
    grid: {
      vertLines: { color: THEME.grid, style: LineStyle.Solid },
      horzLines: { color: THEME.grid, style: LineStyle.Solid },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      mode: isLogScale ? PriceScaleMode.Logarithmic : PriceScaleMode.Normal,
      borderColor: THEME.grid,
    },
    leftPriceScale: {
      visible: false,
      borderColor: THEME.grid,
    },
    timeScale: {
      borderColor: THEME.grid,
      timeVisible: true,
      rightOffset: 2,
      secondsVisible: false,
    },
  })
}

function applyElement(chart: ReturnType<typeof createChart>, el: ChartElement): AppliedElement | null {
  if (!el.x) return null
  if (el.title === "candles_source") return null

  if (isMarkerElement(el)) {
    return {
      series: null,
      markers: buildMarkers(el),
      isCandles: false,
      timeSet: new Set<number>(),
    }
  }

  if (el.kind === "candlestick" || (el.open && el.high && el.low && el.close)) {
    const series = chart.addCandlestickSeries({
      upColor: CANDLE_COLORS.up,
      downColor: CANDLE_COLORS.down,
      borderVisible: false,
      wickUpColor: CANDLE_COLORS.up,
      wickDownColor: CANDLE_COLORS.down,
      priceLineVisible: false,
    })
    const candles = toCandleData(el)
    const timeSet = new Set<number>()
    if (candles.length > 0) {
      for (const point of candles) timeSet.add(point.time)
      series.setData(candles)
    }
    return { series, markers: [], isCandles: true, timeSet }
  }

  const lineData = toLineData(el)
  if (lineData.length === 0) return { series: null, markers: [], isCandles: false, timeSet: new Set<number>() }

  const series = chart.addLineSeries({
    color: getSeriesLineColor(el),
    lineWidth: 2,
    lineVisible: true,
    priceLineVisible: false,
    lastValueVisible: false,
  })
  series.setData(lineData)
  const timeSet = new Set<number>()
  for (const point of lineData) timeSet.add(point.time)
  return { series, markers: [], isCandles: false, timeSet }
}

interface TradingChartProps {
  elements: ChartElement[]
  height?: number
  className?: string
}

export function TradingChart({ elements, height = 350, className }: TradingChartProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const legendItems = getLegendItems(elements)

  useEffect(() => {
    if (!rootRef.current) return
    const root = rootRef.current
    root.innerHTML = ""

    const visibleElements = elements.filter((el) => !el.is_hidden && el.x !== null)
    if (visibleElements.length === 0) return

    const indicatorElements = visibleElements.filter(isIndicatorElement)
    const mainElements = visibleElements.filter((el) => !isIndicatorElement(el))

    const showIndicatorPane = indicatorElements.length > 0 && mainElements.length > 0
    const paneGap = 8
    const usableHeight = showIndicatorPane ? Math.max(height - paneGap, 120) : height

    const mainContainer = document.createElement("div")
    mainContainer.style.width = "100%"
    root.appendChild(mainContainer)

    const indicatorContainer = document.createElement("div")
    if (showIndicatorPane) {
      indicatorContainer.style.width = "100%"
      indicatorContainer.style.marginTop = "8px"
      root.appendChild(indicatorContainer)
    }

    const mainHeight = showIndicatorPane ? Math.round(usableHeight * 0.72) : usableHeight
    const indicatorHeight = showIndicatorPane ? usableHeight - mainHeight : 0

    const mainChart = buildChart(mainContainer, mainHeight, inferIsLogScale(mainElements))
    const indicatorChart = showIndicatorPane
      ? buildChart(indicatorContainer, indicatorHeight, inferIsLogScale(indicatorElements))
      : null

    const targetMain = mainElements.length > 0 ? mainElements : visibleElements
    const markerBuffersMain: ReturnType<typeof buildMarkers> = []
    let markerTargetMain: any = null
    let markerTargetMainTimes = new Set<number>()
    for (const el of targetMain) {
      const applied = applyElement(mainChart, el)
      if (!applied) continue
      if (applied.series && !markerTargetMain) markerTargetMain = applied.series
      if (applied.series && !markerTargetMainTimes.size) markerTargetMainTimes = applied.timeSet
      if (applied.isCandles && applied.series) {
        markerTargetMain = applied.series
        markerTargetMainTimes = applied.timeSet
      }
      if (applied.markers && applied.markers.length > 0) {
        if (applied.series) {
          applied.series.setMarkers(applied.markers.sort((a, b) => a.time - b.time) as any)
        } else {
          markerBuffersMain.push(...applied.markers)
        }
      }
    }
    if (markerBuffersMain.length > 0) {
      if (!markerTargetMain) {
        const markerData = markerBuffersMain.map((m) => ({ time: m.time, value: 1 }))
        markerData.sort((a, b) => a.time - b.time)
        markerTargetMain = mainChart.addLineSeries({
          color: "transparent",
          lineVisible: false,
          priceLineVisible: false,
          lastValueVisible: false,
        })
        markerTargetMain.setData(markerData as any)
        markerTargetMainTimes = new Set<number>(markerData.map((p) => p.time))
      }
      const filteredMarkers = filterMarkersByTimes(markerBuffersMain, markerTargetMainTimes)
      if (filteredMarkers.length > 0) {
        markerTargetMain.setMarkers(filteredMarkers.sort((a, b) => a.time - b.time) as any)
      }
    }

    if (indicatorChart) {
      const markerBuffersIndicator: ReturnType<typeof buildMarkers> = []
      let markerTargetIndicator: any = null
      let markerTargetIndicatorTimes = new Set<number>()
      for (const el of indicatorElements) {
        const applied = applyElement(indicatorChart, el)
        if (!applied) continue
        if (applied.series && !markerTargetIndicator) markerTargetIndicator = applied.series
        if (applied.series && !markerTargetIndicatorTimes.size) markerTargetIndicatorTimes = applied.timeSet
        if (applied.markers && applied.markers.length > 0) {
          if (applied.series) {
            applied.series.setMarkers(applied.markers.sort((a, b) => a.time - b.time) as any)
          } else {
            markerBuffersIndicator.push(...applied.markers)
          }
        }
      }
      if (markerBuffersIndicator.length > 0) {
        if (!markerTargetIndicator) {
          const markerData = markerBuffersIndicator.map((m) => ({ time: m.time, value: 1 }))
          markerData.sort((a, b) => a.time - b.time)
          markerTargetIndicator = indicatorChart.addLineSeries({
            color: "transparent",
            lineVisible: false,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          markerTargetIndicator.setData(markerData as any)
          markerTargetIndicatorTimes = new Set<number>(markerData.map((p) => p.time))
        }
        const filteredMarkers = filterMarkersByTimes(markerBuffersIndicator, markerTargetIndicatorTimes)
        if (filteredMarkers.length > 0) {
          markerTargetIndicator.setMarkers(filteredMarkers.sort((a, b) => a.time - b.time) as any)
        }
      }
    }

    mainChart.timeScale().fitContent()
    if (indicatorChart) indicatorChart.timeScale().fitContent()

    if (indicatorChart) {
      let syncing = false
      const syncTo = (from: ReturnType<typeof createChart>, to: ReturnType<typeof createChart>) => {
        from.timeScale().subscribeVisibleTimeRangeChange((range) => {
          if (!range || syncing) return
          syncing = true
          to.timeScale().setVisibleRange(range)
          syncing = false
        })
      }
      syncTo(mainChart, indicatorChart)
      syncTo(indicatorChart, mainChart)
    }

    const resize = () => {
      const width = root.clientWidth
      mainChart.applyOptions({ width, height: mainHeight })
      if (indicatorChart) indicatorChart.applyOptions({ width, height: indicatorHeight })
    }
    resize()

    const observer = new ResizeObserver(resize)
    observer.observe(root)

    return () => {
      observer.disconnect()
      mainChart.remove()
      if (indicatorChart) indicatorChart.remove()
      root.innerHTML = ""
    }
  }, [elements, height])

  if (elements.length === 0 || elements.every((el) => el.x === null)) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
        No chart data available
      </div>
    )
  }

  return (
    <div className={cn("relative", className)} style={{ width: "100%", height }}>
      <div ref={rootRef} style={{ width: "100%", height }} />
      {legendItems.length > 0 && (
        <div className="pointer-events-none absolute left-3 top-3 z-20 max-w-[300px] rounded-md border border-border/60 bg-[#06142dcc] px-2 py-1 shadow-sm">
          <div className="flex flex-col gap-1">
            {legendItems.map((item) => (
              <div key={item.key} className="flex items-center gap-2 text-[11px] text-[#d6deed]">
                <span className="inline-block h-0.5 w-3 rounded-sm" style={{ backgroundColor: item.color }} />
                <span className="truncate">- {item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
