import type { ChartElement, HistoryRun, ReportData, ReportMeta, SubElement, TableElement } from "@/types"
import { AppSidebar } from "@/components/AppSidebar"
import { ChartAreaInteractive } from "@/components/ChartAreaInteractive"
import { DataTable } from "@/components/DataTable"
import { SectionCards } from "@/components/SectionCards"
import { SiteHeader } from "@/components/SiteHeader"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

// Named element IDs from the backtesting pipeline
const MAIN_CHART_ID = "main-chart"
const SUB_CHART_ID = "sub-chart"
const PORTFOLIO_ID = "backtesting-run-overview"
const TRADES_ID = "list-of-trades-part"

function findByName(elements: SubElement[], name: string): SubElement | undefined {
  return elements.find((el) => el.name === name)
}

function getChartElements(el: SubElement | undefined): ChartElement[] {
  if (!el || el.type !== "chart") return []
  return el.data.elements as ChartElement[]
}

function getTableElements(el: SubElement | undefined): TableElement[] {
  if (!el || el.type !== "table") return []
  return el.data.elements as TableElement[]
}

interface AppProps {
  reportData: ReportData
  meta: ReportMeta
  history?: HistoryRun[]
  currentRunId?: string | null
  onRunChange?: (runId: string | null) => void
  isSwitching?: boolean
  onClearHistories?: () => Promise<void> | void
  isClearingHistory?: boolean
}

export function App({
  reportData,
  meta,
  history,
  currentRunId,
  onRunChange,
  isSwitching,
  onClearHistories,
  isClearingHistory,
}: AppProps) {
  const subElements = reportData.data.sub_elements

  const mainChartEl = findByName(subElements, MAIN_CHART_ID)
  const subChartEl = findByName(subElements, SUB_CHART_ID)
  const portfolioEl = findByName(subElements, PORTFOLIO_ID)
  const tradesEl = findByName(subElements, TRADES_ID)

  const mainChartElements = getChartElements(mainChartEl)
  const subChartElements = getChartElements(subChartEl)
  const portfolioElements = getChartElements(portfolioEl)
  const tradeTableElements = getTableElements(tradesEl)

  const hasMainChart = mainChartElements.some((el) => el.x !== null)
  const hasSubChart = subChartElements.some((el) => el.x !== null)
  const hasPortfolio = portfolioElements.some((el) => el.x !== null)
  const hasHistory = (history?.length ?? 0) > 0
  const selectedRunId = currentRunId ?? history?.[0]?.id ?? null
  const chartElements: ChartElement[] = [
    ...(hasMainChart ? mainChartElements : []),
    ...(hasSubChart ? subChartElements : []),
    ...(hasPortfolio ? portfolioElements : []),
  ]
  const chartGroups = {
    all: chartElements,
    tradesOrders: hasMainChart ? mainChartElements : [],
    indicators: hasSubChart ? subChartElements : [],
    portfolioHistory: hasPortfolio ? portfolioElements : [],
  }

  return (
    <SidebarProvider defaultOpen={hasHistory}>
      {hasHistory && (
        <AppSidebar
          runs={history ?? []}
          selectedRunId={selectedRunId}
          onRunChange={onRunChange}
          onClearHistories={onClearHistories}
          isClearingHistory={isClearingHistory}
          isSwitching={isSwitching}
        />
      )}
      <SidebarInset>
        <SiteHeader isSwitching={isSwitching} />
        <div className={`flex flex-1 flex-col transition-opacity duration-200 ${isSwitching ? "opacity-70" : "opacity-100"}`}>
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <div className="px-4 lg:px-6">
                <SectionCards meta={meta} />
              </div>
              {chartElements.length > 0 && (
                <div className="px-4 lg:px-6">
                  <ChartAreaInteractive
                    title="Performance Overview"
                    description="Interactive charts from the selected backtesting run"
                    groups={chartGroups}
                    height={360}
                  />
                </div>
              )}
              {tradeTableElements.length > 0 && (
                <DataTable tables={tradeTableElements} meta={meta} />
              )}
              <footer className="px-4 lg:px-6 text-xs text-muted-foreground">
                <span>Generated {meta.creation_time}</span>
              </footer>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
