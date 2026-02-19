import { StrictMode, useEffect, useState } from "react"
import ReactDOM from "react-dom/client"
import { App } from "./App"
import "./index.css"
import type { HistoryRun, ReportData, ReportMeta } from "./types"

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: ReportData; meta: ReportMeta; switching?: boolean }

async function loadReport(base: string): Promise<{ data: ReportData; meta: ReportMeta }> {
  const bundle = await fetch(`${base}/report.json`)
  if (bundle.ok) {
    const json = (await bundle.json()) as { data: ReportData; meta: ReportMeta }
    if (json?.data && json?.meta) return json
  }

  const [data, meta] = await Promise.all([
    fetch(`${base}/report_data.json`).then((r) => {
      if (!r.ok) throw new Error(`report_data.json: ${r.status} ${r.statusText}`)
      return r.json() as Promise<ReportData>
    }),
    fetch(`${base}/report_meta.json`).then((r) => {
      if (!r.ok) throw new Error(`report_meta.json: ${r.status} ${r.statusText}`)
      return r.json() as Promise<ReportMeta>
    }),
  ])
  return { data, meta }
}

function Root() {
  const [state, setState] = useState<LoadState>({ status: "loading" })
  const [history, setHistory] = useState<HistoryRun[]>([])
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [clearingHistory, setClearingHistory] = useState(false)

  const refreshHistory = () =>
    fetch("./history.json")
      .then((r) => (r.ok ? (r.json() as Promise<HistoryRun[]>) : Promise.resolve([])))
      .then((runs) => {
        setHistory(runs)
        setCurrentRunId((prev) => (prev && runs.some((run) => run.id === prev) ? prev : (runs[0]?.id ?? null)))
      })

  // Load run history and preselect latest run when available
  useEffect(() => {
    refreshHistory()
      .catch(() => {})
      .finally(() => setHistoryLoaded(true))
  }, [])

  // Load selected history run (latest by default), fallback to current dir when no history exists
  useEffect(() => {
    if (!historyLoaded) return
    setState((prev) => (prev.status === "ready"
      ? { ...prev, switching: true }
      : { status: "loading" }))
    const base = currentRunId ? `./history/${currentRunId}` : "."
    loadReport(base)
      .then(({ data, meta }) => setState({ status: "ready", data, meta, switching: false }))
      .catch((err) =>
        setState((prev) =>
          prev.status === "ready"
            ? { ...prev, switching: false }
            : { status: "error", message: String(err) }
        )
      )
  }, [currentRunId, historyLoaded])

  const clearHistories = async () => {
    setClearingHistory(true)
    try {
      await fetch("./history-clear", { method: "POST" })
      await refreshHistory()
    } finally {
      setClearingHistory(false)
    }
  }

  if (state.status === "loading") {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          color: "#b2b5be",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "1.25rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
            Loading report…
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.6 }}>Fetching backtesting data</div>
        </div>
      </div>
    )
  }

  if (state.status === "error") {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          color: "#b2b5be",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{ fontSize: "1.25rem", fontWeight: "bold", marginBottom: "0.5rem", color: "#ef4444" }}
          >
            Failed to load report
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.7 }}>{state.message}</div>
          <div style={{ fontSize: "0.75rem", marginTop: "0.75rem", opacity: 0.5 }}>
            Make sure report.json (or report_data.json + report_meta.json) is in the expected directory.
          </div>
        </div>
      </div>
    )
  }

  return (
    <StrictMode>
      <App
        reportData={state.data}
        meta={state.meta}
        history={history}
        currentRunId={currentRunId}
        onRunChange={setCurrentRunId}
        isSwitching={state.switching === true}
        onClearHistories={clearHistories}
        isClearingHistory={clearingHistory}
      />
    </StrictMode>
  )
}

ReactDOM.createRoot(document.getElementById("root")!).render(<Root />)
