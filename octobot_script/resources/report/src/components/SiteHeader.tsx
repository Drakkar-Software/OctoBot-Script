import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Loader2 } from "lucide-react"

interface SiteHeaderProps {
  isSwitching?: boolean
}

export function SiteHeader({ isSwitching }: SiteHeaderProps) {
  return (
    <header className="flex h-(--header-height) shrink-0 items-center gap-2 border-b border-border transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mx-2 data-[orientation=vertical]:h-4" />
        <h1 className="text-base font-medium">Backtesting Dashboard</h1>
        <div className="ml-auto flex items-center gap-2">
          {isSwitching && (
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Loader2 className="size-3 animate-spin" />
              Loading
            </span>
          )}
          <Button variant="ghost" asChild size="sm" className="hidden sm:flex">
            <a href="#" className="dark:text-foreground">Backtesting</a>
          </Button>
        </div>
      </div>
    </header>
  )
}
