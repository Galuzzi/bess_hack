import { useState } from "react";
import { BessBanner } from "./BessBanner";
import { BessNavigation } from "./BessNavigation";
import { OverviewSection } from "./OverviewSection";
import { ForecastingSection } from "./ForecastingSection";
import { PredictionsSection } from "./PredictionsSection";

export const BessDashboard = () => {
  const [activeSection, setActiveSection] = useState<string>("overview");

  const renderActiveSection = () => {
    switch (activeSection) {
      case "overview":
        return <OverviewSection />;
      case "forecasting":
        return <ForecastingSection />;
      case "predictions":
        return <PredictionsSection />;
      default:
        return <OverviewSection />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Banner */}
      <BessBanner />
      
      {/* Main Dashboard Layout */}
      <div className="flex">
        {/* Left Navigation */}
        <BessNavigation 
          activeSection={activeSection}
          onSectionChange={setActiveSection}
        />
        
        {/* Main Content Area */}
        <main 
          className="flex-1 min-h-[calc(100vh-8rem)] bg-dashboard-section"
          style={{ display: activeSection ? 'block' : 'none' }}
        >
          {renderActiveSection()}
        </main>
      </div>
    </div>
  );
};