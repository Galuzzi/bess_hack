# BESS Dashboard - Battery Energy Storage System

A professional dashboard for monitoring and managing Battery Energy Storage Systems (BESS) with real-time data visualization, predictive analytics, and risk assessment.

## Project Features

- **Real-time Overview**: Live monitoring with Grafana iframe integration
- **Energy Forecasting**: FastAPI-powered predictive analytics
- **Risk Predictions**: AI-driven risk assessment and maintenance scheduling
- **Accessible Design**: WCAG AA compliant light theme
- **Modular Architecture**: Clean, maintainable React components

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager

### Installation & Development

```bash
# Clone the repository
git clone <your-repo-url>

# Navigate to project directory
cd bess-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:8080`

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Integration Guide

### Grafana Integration
1. Update iframe `src` URLs in the component files with your Grafana instance URLs
2. Configure authentication and proper dashboard permissions
3. Set up alerting rules for critical system thresholds

### FastAPI Backend Integration
1. Replace placeholder API endpoints with your actual FastAPI server URLs
2. Implement proper authentication headers
3. Add error handling and loading states for API calls

### Key Files to Modify:
- `src/components/OverviewSection.tsx` - Update Grafana iframe sources
- `src/components/ForecastingSection.tsx` - Update FastAPI endpoints
- `src/components/PredictionsSection.tsx` - Update both Grafana and FastAPI endpoints

## Architecture

### Components Structure
```
src/
├── components/
│   ├── BessDashboard.tsx      # Main dashboard container
│   ├── BessBanner.tsx         # Top banner with branding
│   ├── BessNavigation.tsx     # Left sidebar navigation
│   ├── OverviewSection.tsx    # Real-time monitoring section
│   ├── ForecastingSection.tsx # Energy forecasting section
│   └── PredictionsSection.tsx # Risk predictions section
├── assets/
│   └── bess-banner.jpg        # Dashboard banner image
└── pages/
    └── Index.tsx              # Main page component
```

### Design System
- Light theme optimized for industrial dashboards
- Professional blue primary color (#3B82F6)
- Energy green secondary color (#059669)
- Accessible contrast ratios (WCAG AA compliant)
- Semantic color tokens defined in `src/index.css`

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **UI Components**: shadcn/ui component library
- **Build Tool**: Vite
- **Routing**: React Router DOM
- **Icons**: Lucide React

## Accessibility

This dashboard follows WCAG 2.1 AA accessibility standards:
- High contrast color ratios
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly labels
- Focus management

## Deployment

### Using Lovable
1. Open your [Lovable Project](https://lovable.dev/projects/0447db2b-b61e-4316-a6d4-f3fc9595973f)
2. Click "Share" → "Publish"

### Manual Deployment
The built files can be deployed to any static hosting service:
- Netlify
- Vercel
- AWS S3 + CloudFront
- GitHub Pages

## Customization

### Colors & Branding
Modify the design system in `src/index.css` and `tailwind.config.ts` to match your brand colors.

### Adding New Sections
1. Create new component in `src/components/`
2. Add navigation item to `BessNavigation.tsx`
3. Add route handling in `BessDashboard.tsx`

### Integration Examples

#### Grafana Iframe Example:
```jsx
<iframe
  src="https://your-grafana.com/d/dashboard-id/embed"
  width="100%"
  height="400"
  frameBorder="0"
/>
```

#### FastAPI Integration Example:
```jsx
const [imageData, setImageData] = useState(null);

useEffect(() => {
  fetch('https://your-fastapi-backend.com/api/forecast/demand')
    .then(response => response.blob())
    .then(blob => setImageData(URL.createObjectURL(blob)));
}, []);

return <img src={imageData} alt="Forecast" />;
```

## Support

For technical support or questions:
- Review the integration guides above
- Check the component documentation in each file
- Refer to [Lovable Documentation](https://docs.lovable.dev/)

## License

This project is built using Lovable and follows their terms of service.