import type { TableColumn, TableElement } from "@/types"
import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ArrowUpDown, ChevronLeft, ChevronRight, Download } from "lucide-react"
import { cn } from "@/lib/utils"

function downloadCsv(name: string, columns: { field: string; label: string }[], rows: Record<string, unknown>[]) {
  const header = columns.map((c) => c.label).join(",")
  const body = rows
    .map((row) =>
      columns
        .map((c) => {
          const v = row[c.field]
          return typeof v === "string" ? v.replaceAll(",", " ") : String(v ?? "")
        })
        .join(",")
    )
    .join("\n")
  const blob = new Blob([`${header}\n${body}`], { type: "text/csv" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `${name}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

/** Detects if a column is a time/date column (should not be colorized by value sign). */
function isTimeColumn(col: TableColumn): boolean {
  const name = `${col.field} ${col.label}`.toLowerCase()
  return name.includes("time") || name.includes("date") || name.includes("timestamp")
}

/** Detects if a column represents trade side (buy/sell). */
function isSideColumn(col: TableColumn): boolean {
  const name = `${col.field} ${col.label}`.toLowerCase()
  return name.includes("side") || name.includes("trade_type") || name.includes("order_type")
}

/** Returns "buy" | "sell" | null for a side column value. */
function parseSide(value: unknown): "buy" | "sell" | null {
  const str = String(value ?? "").toLowerCase()
  if (str.includes("buy") || str === "long") return "buy"
  if (str.includes("sell") || str === "short") return "sell"
  return null
}

/** Determines a row's trade side from its data. */
function getRowSide(
  row: Record<string, unknown>,
  sideColField: string | null
): "buy" | "sell" | null {
  if (!sideColField) return null
  return parseSide(row[sideColField])
}

/** Regular value cell — foreground for positive, red for negative. */
function ValueCell({ value }: { value: unknown }) {
  const str = String(value ?? "—")
  const isPos = typeof value === "number" ? value > 0 : str.startsWith("+")
  const isNeg = typeof value === "number" ? value < 0 : str.startsWith("-")
  return (
    <span className={cn(isPos && "text-foreground", isNeg && "text-destructive")}>
      {str}
    </span>
  )
}

/** Side badge cell — buy in foreground colors, sell in red. */
function SideCell({ value }: { value: unknown }) {
  const side = parseSide(value)
  const label = String(value ?? "—")
  return (
    <span
      className={cn(
        "inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wide",
        side === "buy" && "bg-primary/15 text-foreground",
        side === "sell" && "bg-red-500/15 text-red-400",
        !side && "text-muted-foreground"
      )}
    >
      {label}
    </span>
  )
}

interface SingleTableProps {
  table: TableElement
}

function SingleTable({ table }: SingleTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState("")
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 20 })

  const sideCol = table.columns.find(isSideColumn)
  const sideField = sideCol?.field ?? null
  const timeFields = new Set(table.columns.filter(isTimeColumn).map((c) => c.field))
  const sideFields = new Set(table.columns.filter(isSideColumn).map((c) => c.field))

  const columns: ColumnDef<Record<string, unknown>>[] = table.columns.map((col) => ({
    accessorKey: col.field,
    header: ({ column }) => (
      <button
        type="button"
        className="flex items-center gap-1 hover:text-foreground transition-colors"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        {col.label}
        <ArrowUpDown className="size-3 opacity-50" />
      </button>
    ),
    cell: ({ getValue }) => {
      const value = getValue()
      if (sideFields.has(col.field)) return <SideCell value={value} />
      if (timeFields.has(col.field)) return <span className="text-muted-foreground">{String(value ?? "—")}</span>
      return <ValueCell value={value} />
    },
  }))

  const reactTable = useReactTable({
    data: table.rows,
    columns,
    state: { sorting, globalFilter, pagination },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  const totalPages = reactTable.getPageCount()
  const currentPage = reactTable.getState().pagination.pageIndex

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-sm font-semibold text-foreground capitalize">
          {table.title.replaceAll("_", " ")}
        </h3>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Filter…"
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="h-8 px-3 rounded-md border border-input bg-background text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring w-40"
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() =>
              downloadCsv(
                table.title,
                table.columns.map((c) => ({ field: c.field, label: c.label })),
                reactTable.getFilteredRowModel().rows.map((r) => r.original)
              )
            }
          >
            <Download className="size-3.5" />
            Export
          </Button>
        </div>
      </div>

      <Table>
        <TableHeader>
          {reactTable.getHeaderGroups().map((hg) => (
            <TableRow key={hg.id}>
              {hg.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {reactTable.getRowModel().rows.length > 0 ? (
            reactTable.getRowModel().rows.map((row) => {
              const side = getRowSide(row.original, sideField)
              return (
                <TableRow
                  key={row.id}
                  className={cn(
                    side === "buy" && "bg-primary/10 hover:bg-primary/15",
                    side === "sell" && "bg-red-950/30 hover:bg-red-950/50"
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              )
            })
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="text-center text-muted-foreground py-8">
                No data
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {reactTable.getFilteredRowModel().rows.length} row
            {reactTable.getFilteredRowModel().rows.length !== 1 ? "s" : ""}
          </span>
          <div className="flex items-center gap-1">
            <Button
              size="icon"
              variant="ghost"
              onClick={() => reactTable.previousPage()}
              disabled={!reactTable.getCanPreviousPage()}
            >
              <ChevronLeft className="size-4" />
            </Button>
            <span className="px-2">
              {currentPage + 1} / {totalPages}
            </span>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => reactTable.nextPage()}
              disabled={!reactTable.getCanNextPage()}
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

interface TradesTableProps {
  elements: TableElement[]
}

export function TradesTable({ elements }: TradesTableProps) {
  if (elements.length === 0) return null

  return (
    <div className="flex flex-col gap-8">
      {elements.map((table, i) => (
        <SingleTable key={i} table={table} />
      ))}
    </div>
  )
}
