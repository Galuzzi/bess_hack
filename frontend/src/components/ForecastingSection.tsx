import { useState, useEffect } from "react";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export const ForecastingSection = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [images, setImages] = useState<{[key: string]: string}>({});

  const forecastImages = [
    {
      id: "energy-demand",
      title: "Energy Demand Forecast",
      description: "24-hour ahead prediction of energy demand patterns based on historical data, weather conditions, and grid requirements.",
      apiEndpoint: "http://localhost:8000/plot-soc", // <-- updated to local FastAPI endpoint
      placeholder: "Demand forecast chart will be displayed here"
    },
    {
      id: "price-optimization", 
      title: "Price Optimization Forecast",
      description: "Real-time energy price predictions and optimal charge/discharge timing recommendations for maximum cost efficiency.",
      apiEndpoint: "http://localhost:8000/plot-revenue", // <-- updated to local FastAPI endpoint
      placeholder: "Price optimization visualization will be displayed here"
    }
  ];

  useEffect(() => {
    forecastImages.forEach(async (forecast) => {
      const dateStr = selectedDate ? format(selectedDate, "yyyy-MM-dd") : "";
      const url = `${forecast.apiEndpoint}?date=${dateStr}`;
      try {
        const res = await fetch(url);
        if (res.ok) {
          const blob = await res.blob();
          const imgUrl = URL.createObjectURL(blob);
          setImages(prev => ({ ...prev, [forecast.id]: imgUrl }));
        }
      } catch (err) {
        // handle error if needed
      }
    });
  // re-fetch when selectedDate changes
  }, [selectedDate]);

  return (
    <div className="p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Energy Forecasting</h2>
        <p className="text-muted-foreground">
          Advanced predictive analytics for optimal energy storage management and grid integration
        </p>
      </div>

      {/* Date Selector */}
      <div className="flex justify-center mb-8">
        <div className="bg-card rounded-lg border shadow-sm p-6">
          <div className="text-center mb-4">
            <h3 className="text-lg font-semibold text-foreground mb-2">Select Forecast Date</h3>
            <p className="text-sm text-muted-foreground">Choose a date to generate forecasting predictions</p>
          </div>
          <div className="flex justify-center">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-[240px] justify-start text-left font-normal",
                    !selectedDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {selectedDate ? format(selectedDate, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="center">
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  initialFocus
                  className={cn("p-3 pointer-events-auto")}
                />
              </PopoverContent>
            </Popover>
          </div>
          <div className="text-center mt-4">
            <p className="text-xs text-muted-foreground">
              Selected date will be sent to API: {selectedDate ? format(selectedDate, "yyyy-MM-dd") : "None"}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {forecastImages.map((forecast) => (
          <div key={forecast.id} className="bg-card rounded-lg border shadow-sm overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b bg-gradient-to-r from-primary/5 to-secondary/5">
              <h3 className="text-xl font-semibold text-card-foreground mb-2">
                {forecast.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {forecast.description}
              </p>
            </div>

            {/* Image Display Area */}
            <div className="p-6">
              <div className="aspect-video w-full bg-muted rounded-lg border-2 border-dashed border-border flex flex-col items-center justify-center">
                {images[forecast.id] ? (
                  <img
                    src={images[forecast.id]}
                    alt={forecast.title}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-center text-muted-foreground space-y-2">
                    <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center mb-4">
                      <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div className="text-sm font-medium">FastAPI Image Placeholder</div>
                    <div className="text-xs opacity-75">{forecast.placeholder}</div>
                  </div>
                )}
              </div>
            </div>

            {/* API Information */}
            <div className="px-6 pb-6">
              <div className="bg-muted/30 rounded-lg p-4">
                <div className="text-xs text-muted-foreground mb-1">API Endpoint:</div>
                <code className="text-xs bg-background px-2 py-1 rounded border font-mono">
                  {forecast.apiEndpoint}
                </code>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Integration Instructions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-secondary/10 rounded-lg p-6 border border-secondary/20">
          <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center">
            <svg className="w-5 h-5 text-secondary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Implementation Notes
          </h4>
          <ul className="text-sm text-muted-foreground space-y-2">
            <li>• Replace placeholder divs with actual image elements</li>
            <li>• Connect to your FastAPI backend endpoints</li>
            <li>• Add loading states and error handling</li>
            <li>• Consider implementing auto-refresh intervals</li>
          </ul>
        </div>

        <div className="bg-accent/10 rounded-lg p-6 border border-accent/20">
          <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center">
            <svg className="w-5 h-5 text-accent mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Forecast Features
          </h4>
          <ul className="text-sm text-muted-foreground space-y-2">
            <li>• 24-hour energy demand predictions</li>
            <li>• Weather-integrated forecasting</li>
            <li>• Grid price optimization</li>
            <li>• Automated charging schedules</li>
          </ul>
        </div>
      </div>
    </div>
  );
};