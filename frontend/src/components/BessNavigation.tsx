import { useState } from "react";
import { Button } from "@/components/ui/button";
import { BarChart3, TrendingUp, AlertTriangle } from "lucide-react";

interface BessNavigationProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export const BessNavigation = ({ activeSection, onSectionChange }: BessNavigationProps) => {
  const navigationItems = [
    {
      id: "overview",
      label: "Overview",
      icon: BarChart3,
      description: "Real-time BESS monitoring"
    },
    {
      id: "forecasting", 
      label: "Forecasting",
      icon: TrendingUp,
      description: "Energy predictions & analysis"
    },
    {
      id: "predictions",
      label: "Risk Predictions", 
      icon: AlertTriangle,
      description: "Risk assessment & alerts"
    }
  ];

  return (
    <nav className="w-64 bg-dashboard-nav border-r border-border h-full">
      <div className="p-4">
        <h2 className="text-lg font-semibold text-foreground mb-6">
          Dashboard Navigation
        </h2>
        <div className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                className={`w-full justify-start text-left h-auto p-4 ${
                  isActive 
                    ? "bg-primary text-primary-foreground" 
                    : "hover:bg-dashboard-nav-hover"
                }`}
                onClick={() => onSectionChange(item.id)}
              >
                <div className="flex items-start space-x-3">
                  <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-medium">{item.label}</div>
                    <div className={`text-sm ${
                      isActive ? "text-primary-foreground/80" : "text-muted-foreground"
                    }`}>
                      {item.description}
                    </div>
                  </div>
                </div>
              </Button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};