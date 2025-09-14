export const OverviewSection = () => {
  const grafanaIframes = [
    {
      id: "system-status",
      title: "State Of Charge",
      src: "http://localhost:3000/d-solo/a1ce40a4-3e62-4939-a48c-1343d0083aa1/security-and-incident-management?orgId=1&from=1749856200000&to=1749858900000&timezone=browser&var-datasource=aexz24qqeaoe8e&refresh=10s&showCategory=Value%20mappings&theme=light&panelId=5&__feature.dashboardSceneSolo=true",
      height: "100%",
      with: "100%"
    },
    {
      id: "power-flow",
      title: "Real-time Power Flow",
      src: "http://localhost:3000/d-solo/a1ce40a4-3e62-4939-a48c-1343d0083aa1/security-and-incident-management?orgId=1&from=1749856200000&to=1749858900000&timezone=browser&var-datasource=aexz24qqeaoe8e&refresh=10s&showCategory=Value%20mappings&theme=light&panelId=6&__feature.dashboardSceneSolo=true",
      height: "100%",
      with: "100%"
    },
    {
      id: "battery-metrics",
      title: "State Of Health",
      src: "http://localhost:3000/d-solo/a1ce40a4-3e62-4939-a48c-1343d0083aa1/security-and-incident-management?orgId=1&from=1749856200000&to=1749858900000&timezone=browser&var-datasource=aexz24qqeaoe8e&refresh=10s&showCategory=Value%20mappings&theme=light&panelId=7&__feature.dashboardSceneSolo=true",
      height: "100%",
      with: "100%"
    },
    {
      id: "grid-connection",
      title: "Charging Status",
      src: "http://localhost:3000/d-solo/a1ce40a4-3e62-4939-a48c-1343d0083aa1/security-and-incident-management?orgId=1&from=1749856200000&to=1749858900000&timezone=browser&var-datasource=aexz24qqeaoe8e&refresh=10s&showCategory=Value%20mappings&theme=light&panelId=8&__feature.dashboardSceneSolo=true",
      height: "100%",
      with: "100%"
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

        {/* Right column - 4 columns */}
          {grafanaIframes.map((frames, index) => (

              <div className="col-span-4 space-y-4">
          {/* System Status */}
          <div className="bg-card rounded-lg border shadow-sm">
            <div className="p-3 border-b">
              <h3 className="text-sm font-semibold text-card-foreground">
                {frames.title}
              </h3>
            </div>
            <div className="p-3">
              <div
                className="w-full bg-muted rounded border-2 border-dashed border-border flex items-center justify-center"
                style={{ height: frames.height, width: frames.width }}
              >
                  <iframe src={frames.src}></iframe>
              </div>
            </div>
          </div>
              </div>
          ))}
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