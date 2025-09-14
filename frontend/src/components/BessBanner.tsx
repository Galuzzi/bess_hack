import bessBannerImage from "@/assets/bess-banner.jpg";

export const BessBanner = () => {
  return (
    <div className="relative h-32 w-full overflow-hidden bg-dashboard-header">
      <img 
        src={bessBannerImage} 
        alt="Battery Energy Storage System facility with monitoring displays"
        className="w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-primary/80 flex items-center">
        <div className="max-w-7xl mx-auto px-6 text-primary-foreground">
          <h1 className="text-3xl font-bold mb-2">
            Battery Energy Storage System Dashboard
          </h1>
          <p className="text-lg opacity-90">
            Real-time monitoring, predictive analysis, and intelligent forecasting for optimal energy management
          </p>
        </div>
      </div>
    </div>
  );
};