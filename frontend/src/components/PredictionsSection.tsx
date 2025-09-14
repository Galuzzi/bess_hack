export const PredictionsSection = () => {
  const predictionDashboards = [
    {
      id: "thermal-risk",
      title: "Thermal Risk Assessment", 
      type: "grafana",
      src: "https://your-grafana-instance.com/d/thermal-risk/embed",
      height: "350px",
      description: "Battery temperature monitoring and overheating risk prediction"
    },
    {
      id: "degradation-analysis",
      title: "Battery Degradation Prediction",
      type: "fastapi", 
      apiEndpoint: "https://your-fastapi-backend.com/api/predictions/degradation",
      height: "300px",
      description: "Long-term battery health and capacity degradation forecasting"
    },
    {
      id: "grid-instability",
      title: "Grid Instability Alerts",
      type: "grafana",
      src: "https://your-grafana-instance.com/d/grid-instability/embed", 
      height: "320px",
      description: "Grid connection stability and potential fault detection"
    },
    {
      id: "maintenance-schedule",
      title: "Maintenance Predictions",
      type: "fastapi",
      apiEndpoint: "https://your-fastapi-backend.com/api/predictions/maintenance",
      height: "280px",
      description: "Predictive maintenance scheduling based on component wear analysis"
    },
    {
      id: "safety-monitoring",
      title: "Safety System Monitoring",
      type: "grafana",
      src: "https://your-grafana-instance.com/d/safety-monitoring/embed",
      height: "300px", 
      description: "Real-time safety system status and emergency response protocols"
    },
    {
      id: "performance-anomaly",
      title: "Performance Anomaly Detection",
      type: "fastapi",
      apiEndpoint: "https://your-fastapi-backend.com/api/predictions/anomalies",
      height: "340px",
      description: "AI-powered detection of unusual performance patterns and efficiency drops"
    }
  ];

  const renderPredictionCard = (prediction: typeof predictionDashboards[0]) => (
    <div key={prediction.id} className="bg-card rounded-lg border shadow-sm">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-card-foreground">
            {prediction.title}
          </h3>
          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
            prediction.type === 'grafana' 
              ? 'bg-primary/10 text-primary' 
              : 'bg-secondary/10 text-secondary'
          }`}>
            {prediction.type.toUpperCase()}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          {prediction.description}
        </p>
      </div>
      
      <div className="p-4">
        <div 
          className="w-full bg-muted rounded border-2 border-dashed border-border flex flex-col items-center justify-center"
          style={{ height: prediction.height }}
        >
          {prediction.type === 'grafana' ? (
            <div className="text-center text-muted-foreground">
              <div className="w-12 h-12 mx-auto bg-primary/10 rounded-full flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="text-sm font-medium mb-1">Grafana Dashboard</div>
              <div className="text-xs opacity-75">src: {prediction.src}</div>
            </div>
          ) : (
            <div className="text-center text-muted-foreground">
              <div className="w-12 h-12 mx-auto bg-secondary/10 rounded-full flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="text-sm font-medium mb-1">FastAPI Prediction</div>
              <div className="text-xs opacity-75">API: {prediction.apiEndpoint}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Risk Predictions & Analysis</h2>
        <p className="text-muted-foreground">
          Advanced AI-powered risk assessment and predictive maintenance for optimal BESS operation
        </p>
      </div>

      {/* Alert Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-accent/10 border border-accent/20 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-accent/20 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-medium text-foreground">Active Alerts</div>
              <div className="text-2xl font-bold text-accent">3</div>
            </div>
          </div>
        </div>

        <div className="bg-secondary/10 border border-secondary/20 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-secondary/20 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-medium text-foreground">System Health</div>
              <div className="text-2xl font-bold text-secondary">98%</div>
            </div>
          </div>
        </div>

        <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-medium text-foreground">Next Maintenance</div>
              <div className="text-2xl font-bold text-primary">15d</div>
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Dashboards Grid */}
      <div className="grid grid-cols-12 gap-4">
        {/* Top row: 2 large cards */}
        <div className="col-span-6">
          {renderPredictionCard(predictionDashboards[0])}
        </div>
        <div className="col-span-6">
          {renderPredictionCard(predictionDashboards[1])}
        </div>

        {/* Middle row: 3 medium cards */}
        <div className="col-span-4">
          {renderPredictionCard(predictionDashboards[2])}
        </div>
        <div className="col-span-4">
          {renderPredictionCard(predictionDashboards[3])}
        </div>
        <div className="col-span-4">
          {renderPredictionCard(predictionDashboards[4])}
        </div>

        {/* Bottom: 1 full-width card */}
        <div className="col-span-12">
          {renderPredictionCard(predictionDashboards[5])}
        </div>
      </div>

      {/* Integration Guide */}
      <div className="mt-8 bg-muted/30 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-foreground mb-4">Integration Guide</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-muted-foreground">
          <div>
            <h5 className="font-medium text-foreground mb-2">Grafana Integration:</h5>
            <ul className="space-y-1">
              <li>• Update iframe src URLs with your Grafana instance</li>
              <li>• Configure proper authentication and permissions</li>
              <li>• Set up alerting rules for critical thresholds</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium text-foreground mb-2">FastAPI Integration:</h5>
            <ul className="space-y-1">
              <li>• Replace placeholder endpoints with actual API URLs</li>
              <li>• Implement proper error handling and loading states</li>
              <li>• Add authentication headers for secure access</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};