export const OverviewSection = () => {
  const grafanaIframes = [
    {
      id: "system-status",
      title: "System Status Overview",
      src: "https://your-grafana-instance.com/d/system-status/embed",
      height: "300px"
    },
    {
      id: "power-flow",
      title: "Real-time Power Flow",
      src: "https://your-grafana-instance.com/d/power-flow/embed", 
      height: "400px"
    },
    {
      id: "battery-metrics",
      title: "Battery Performance Metrics",
      src: "https://your-grafana-instance.com/d/battery-metrics/embed",
      height: "350px"
    },
    {
      id: "grid-connection",
      title: "Grid Connection Status",
      src: "https://your-grafana-instance.com/d/grid-status/embed",
      height: "300px"
    },
    {
      id: "environmental",
      title: "Environmental Conditions",
      src: "https://your-grafana-instance.com/d/environmental/embed",
      height: "280px"
    },
    {
      id: "alerts",
      title: "System Alerts & Warnings",
      src: "https://your-grafana-instance.com/d/alerts/embed",
      height: "250px"
    }
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">Real-time Overview</h2>
        <p className="text-muted-foreground">
          Live monitoring of BESS performance, power flow, and system health
        </p>
      </div>
      
      {/* Grid layout optimized for visual appeal */}
      <div className="grid grid-cols-12 gap-4">
        {/* Large main dashboard - spans 8 columns */}
        <div className="col-span-8">
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold text-card-foreground">
                {grafanaIframes[1].title}
              </h3>
            </div>
            <div className="p-4">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[1].height }}
              >
                <div className="text-center text-muted-foreground">
                  <div className="text-sm font-medium mb-1">Grafana Iframe Placeholder</div>
                  <div className="text-xs">src: {grafanaIframes[1].src}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right column - 4 columns */}
        <div className="col-span-4 space-y-4">
          {/* System Status */}
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold text-card-foreground">
                {grafanaIframes[0].title}
              </h3>
            </div>
            <div className="p-3">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[0].height }}
              >
                <div className="text-center text-muted-foreground text-xs">
                  <div className="font-medium mb-1">Grafana Iframe</div>
                  <div>System Status</div>
                </div>
              </div>
            </div>
          </div>

          {/* Grid Connection */}
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold text-card-foreground">
                {grafanaIframes[3].title}
              </h3>
            </div>
            <div className="p-3">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[3].height }}
              >
                <div className="text-center text-muted-foreground text-xs">
                  <div className="font-medium mb-1">Grafana Iframe</div>
                  <div>Grid Status</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom row - Battery Metrics spans 6, Environmental spans 3, Alerts spans 3 */}
        <div className="col-span-6">
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold text-card-foreground">
                {grafanaIframes[2].title}
              </h3>
            </div>
            <div className="p-4">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[2].height }}
              >
                <div className="text-center text-muted-foreground">
                  <div className="text-sm font-medium mb-1">Grafana Iframe Placeholder</div>
                  <div className="text-xs">Battery Performance Data</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-3">
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold text-card-foreground">
                {grafanaIframes[4].title}
              </h3>
            </div>
            <div className="p-3">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[4].height }}
              >
                <div className="text-center text-muted-foreground text-xs">
                  <div className="font-medium mb-1">Environmental</div>
                  <div>Temperature, Humidity</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-3">
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold text-card-foreground">
                {grafanaIframes[5].title}
              </h3>
            </div>
            <div className="p-3">
              <div 
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: grafanaIframes[5].height }}
              >
                <div className="text-center text-muted-foreground text-xs">
                  <div className="font-medium mb-1">System Alerts</div>
                  <div>Warnings & Status</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-muted/50 rounded-lg">
        <p className="text-sm text-muted-foreground">
          <strong>Integration Note:</strong> Replace the placeholder divs above with actual Grafana iframe embeds.
          Update the `src` attributes in the grafanaIframes array with your Grafana dashboard URLs.
        </p>
      </div>
    </div>
  );
};