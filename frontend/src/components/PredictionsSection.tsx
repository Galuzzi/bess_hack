// src/components/PredictionsSection.tsx
// Named export expected by BessDashboard.tsx: { PredictionsSection }

export const PredictionsSection = () => {
  // Base and panel URLs (your working links)
  const BASE =
    "http://localhost:3000/d-solo/a1ce40a4-3e62-4939-a48c-1343d0083aa1/security-and-incident-management?orgId=1&timezone=browser&theme=light&__feature.dashboardSceneSolo=true&kiosk";

  const urls = {
    gauges: `${BASE}&from=1737723900000&to=1748088300000&panelId=1`,
    latest: `${BASE}&from=1737723900000&to=1748088300000&panelId=2`,
    table:  `${BASE}&from=1737723900000&to=1748088300000&panelId=3`,
    chart:  `${BASE}&from=1735650300000&to=1740402300000&panelId=4`,
  };

  return (
    <div className="p-6">
      {/* Current Status */}
      <h2 className="text-2xl font-bold text-foreground mb-3">Current Status</h2>
      <div className="bg-card rounded-lg border shadow-sm mb-6">
        <div className="px-4 pt-4">
          <h3 className="text-lg font-semibold text-foreground">Key Indicators</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Live gauges for CO, VOC, fire alarm temperature, and BESS temperature vs. safety thresholds.
          </p>
        </div>
        <div className="p-4">
          <div
            className="w-full bg-muted rounded border overflow-hidden"
            style={{ height: 250 }}
          >
            <iframe
              title="Key Indicators"
              src={urls.gauges}
              className="w-full h-full border-0"
            />
          </div>
        </div>
      </div>

      {/* Incidents & Alerts */}
      <h2 className="text-2xl font-bold text-foreground mb-3">Incidents &amp; Alerts</h2>

      {/* Latest alert (highlighted) */}
      <div
        className="bg-card rounded-lg border shadow-sm mb-4"
        style={{
          background: "linear-gradient(0deg, rgba(37,99,235,0.08), rgba(37,99,235,0.08))",
          borderColor: "rgba(37,99,235,0.20)",
        }}
      >
        <div className="px-4 pt-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-primary" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 3a6 6 0 0 0-6 6v2.3c0 .6-.23 1.17-.64 1.6L4 15h16l-1.36-2.1a2.3 2.3 0 0 1-.64-1.6V9a6 6 0 0 0-6-6Z" stroke="currentColor" strokeWidth="1.6"/>
            <path d="M9.5 18a2.5 2.5 0 0 0 5 0" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
          </svg>
          <h3 className="text-lg font-semibold text-foreground">Latest Alert</h3>
        </div>
        <div className="p-4">
          <div
            className="w-full bg-muted rounded border overflow-hidden"
            style={{ height: 50 }}
          >
            <iframe
              title="Latest Alert"
              src={urls.latest}
              className="w-full h-full border-0"
            />
          </div>
        </div>
      </div>

      {/* Incident table */}
      <div className="bg-card rounded-lg border shadow-sm mb-6">
        <div className="px-4 pt-4">
          <h3 className="text-lg font-semibold text-foreground">Incident History</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Chronological list of warnings with measured values versus thresholds for fast triage.
          </p>
        </div>
        <div className="p-4">
          <div
            className="w-full bg-muted rounded border overflow-hidden"
            style={{ height: 300 }}
          >
            <iframe
              title="Incident History Table"
              src={urls.table}
              className="w-full h-full border-0"
            />
          </div>
        </div>
      </div>

      {/* Incident Analysis */}
      <h2 className="text-2xl font-bold text-foreground mb-3">Incident Analysis</h2>
      <div className="bg-card rounded-lg border shadow-sm">
        <div className="px-4 pt-4">
          <h3 className="text-lg font-semibold text-foreground">Trends Over Time</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Long-range view across safety metrics to catch drift, seasonality, and recurring issues.
          </p>
        </div>
        <div className="p-4">
          <div
            className="w-full bg-muted rounded border overflow-hidden"
            style={{ height: 420 }}
          >
            <iframe
              title="Time-series Trends"
              src={urls.chart}
              className="w-full h-full border-0"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
