import type * as React from "react"
import { History, Loader2, Trash2, TrendingUp } from "lucide-react"
import type { HistoryRun } from "@/types"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  runs: HistoryRun[]
  selectedRunId?: string | null
  onRunChange?: (runId: string | null) => void
  onClearHistories?: () => Promise<void> | void
  isClearingHistory?: boolean
  isSwitching?: boolean
}

export function AppSidebar({
  runs,
  selectedRunId,
  onRunChange,
  onClearHistories,
  isClearingHistory,
  isSwitching,
  ...props
}: AppSidebarProps) {
  const onClearAll = async () => {
    if (!onClearHistories) return
    const confirmed = window.confirm(
      "Delete all saved backtesting history snapshots from every backtesting run?\n\nThis cannot be undone."
    )
    if (!confirmed) return
    await onClearHistories()
  }

  return (
    <Sidebar collapsible="offcanvas" variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" className="data-[slot=sidebar-menu-button]:!p-1.5" isActive>
              <TrendingUp className="!size-5" />
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">OctoBot Script</span>
                <span className="truncate text-xs text-muted-foreground">Report Workspace</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        <Separator className="my-2" />
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel>
            <History className="size-3.5" />
            Backtesting History
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {runs.map((run) => (
                <SidebarMenuItem key={run.id}>
                  <SidebarMenuButton
                    tooltip={run.creation_time}
                    variant="outline"
                    isActive={selectedRunId === run.id}
                    onClick={() => onRunChange?.(run.id)}
                    className="h-auto items-start py-2 transition-all"
                    disabled={isSwitching || isClearingHistory}
                  >
                    <div className="min-w-0">
                      <div className="text-xs font-medium truncate">{run.creation_time}</div>
                      <div className="text-[11px] text-muted-foreground truncate">{run.run_name ?? run.title}</div>
                      {run.summary?.profitability && (
                        <div className="text-[11px] text-foreground/90 truncate">
                          {run.summary.profitability}
                        </div>
                      )}
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton disabled>
              <History className="size-4" />
              <span>{runs.length} runs</span>
              <Badge variant="secondary" className="ml-auto text-[10px]">Saved</Badge>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <Button
              variant="destructive"
              size="sm"
              className="w-full justify-start"
              onClick={onClearAll}
              disabled={isClearingHistory}
            >
              {isClearingHistory ? <Loader2 className="size-3.5 animate-spin" /> : <Trash2 className="size-3.5" />}
              Remove Histories
            </Button>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
