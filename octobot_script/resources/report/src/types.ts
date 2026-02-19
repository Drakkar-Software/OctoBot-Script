export interface ChartElement {
  kind: string
  x: (number | string)[] | null
  y: number[] | null
  open: number[] | null
  high: number[] | null
  low: number[] | null
  close: number[] | null
  volume: number[] | null
  x_type: string | null
  y_type: string | null
  title: string
  text: string[] | null
  mode: string | null
  line_shape: string | null
  own_xaxis: boolean
  own_yaxis: boolean
  color: string | string[] | null
  size: number | number[] | null
  symbol: string | string[] | null
  type: string
  html: string | null
  is_hidden: boolean | null
  opacity: number | null
}

export interface TableColumn {
  field: string
  label: string
  attr: string | null
  render: string | null
}

export interface TableSearch {
  field: string
  label: string
  type: string | null
  options: unknown
}

export interface TableElement {
  title: string
  columns: TableColumn[]
  rows: Record<string, unknown>[]
  searches: TableSearch[]
}

export interface ValueElement {
  title: string | null
  value: string | null
  html: string | null
}

export interface SubElementData {
  sub_elements: SubElement[]
  elements: ChartElement[] | TableElement[] | ValueElement[]
}

export interface SubElement {
  name: string
  type: "chart" | "table" | "value"
  data: SubElementData
}

export interface ReportData {
  name: string
  type: string
  data: {
    sub_elements: SubElement[]
    elements: unknown[]
  }
}

export interface ReportMeta {
  title: string
  creation_time: string
  strategy_config: Record<string, string>
  symbols?: string[]
  time_frames?: string[]
  exchanges?: string[]
  summary?: {
    profitability?: string | null
    portfolio?: string | null
    metrics?: Record<string, string>
  }
}

export interface HistoryRun {
  id: string
  title: string
  creation_time: string
  run_name?: string
  summary?: {
    profitability?: string | null
    portfolio?: string | null
  }
}
