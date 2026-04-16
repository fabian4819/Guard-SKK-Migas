# 🛡️ GUARD Dashboard - Next.js/React Version

A modern, flexible React/Next.js dashboard for the GUARD (Generative Understanding for Anomaly Response & Detection) system monitoring CPP Donggi Booster Compressor.

## ✨ Features

- **Real-time Simulation**: Live playback of historical anomaly detection data
- **Interactive Charts**: Customizable charts using Recharts
  - MAE Timeline with anomaly markers
  - Multi-sensor readings visualization
- **Anomaly Alerts**: Real-time anomaly detection and alert tracking
- **AI Chatbot**: Interactive assistant for querying data and getting help
- **Flexible Controls**:
  - Date range selection
  - Playback speed control (Real-time to Maximum speed)
  - Start/Stop/Reset controls
- **Fully Customizable UI**: Built with TailwindCSS for easy styling
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- CSV data file at `../KODE_FIX/KODE FIX/AnomalyDetected_Test.csv`

### Installation

```bash
# Navigate to the dashboard directory
cd guard-dashboard

# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
guard-dashboard/
├── app/
│   ├── api/
│   │   └── data/
│   │       └── route.ts          # API endpoint for data
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Main dashboard page
│   └── globals.css               # Global styles
├── components/
│   ├── StatsCard.tsx             # Statistics card component
│   ├── ControlPanel.tsx          # Simulation controls
│   ├── MAEChart.tsx              # MAE timeline chart
│   ├── SensorChart.tsx           # Sensor readings chart
│   ├── AlertsPanel.tsx           # Anomaly alerts panel
│   └── Chatbot.tsx               # AI chatbot assistant
├── lib/
│   └── dataLoader.ts             # CSV data loading utility
├── types/
│   └── index.ts                  # TypeScript type definitions
└── README.md
```

## 🎨 Customization

### Styling

The dashboard uses TailwindCSS for styling. You can customize:

1. **Colors**: Edit `tailwind.config.ts` to change the color scheme
2. **Components**: Modify individual component files in `/components`
3. **Layout**: Adjust spacing, sizing, and layout in `app/page.tsx`

### Charts

Charts use Recharts library. Customize:

- Chart types (Line, Bar, Area, etc.)
- Colors and styling
- Tooltips and legends
- Axis configuration

Example - Change MAE chart color:
```tsx
// In MAEChart.tsx
<Line stroke="#YOUR_COLOR" />
```

### Adding New Features

1. **New API Endpoints**: Add routes in `app/api/`
2. **New Components**: Create in `components/` directory
3. **New Data Sources**: Extend `lib/dataLoader.ts`

## 📊 Data Format

The dashboard expects CSV data with these columns:

```
datetime, status, MAE, threshold_ratio, exceed_percent, is_anomaly,
Flow_Rate, Suction_Pressure, Discharge_Pressure, Suction_Temperature,
Discharge_Temperature, [contribution columns], [deviation columns],
Production_Loss_MMSCFD, Gas_Loss_MMSCF
```

## 🔧 Configuration

### API Endpoint

The data API is available at `/api/data` with query parameters:
- `startDate`: Filter start date (YYYY-MM-DD)
- `endDate`: Filter end date (YYYY-MM-DD)
- `limit`: Number of records to return
- `offset`: Pagination offset

### Environment Variables

Create `.env.local` for configuration:

```env
# Add any environment variables here
# Example:
# NEXT_PUBLIC_API_URL=http://your-api.com
```

## 🆚 Comparison with Streamlit Version

| Feature | Streamlit | Next.js/React |
|---------|-----------|---------------|
| **Flexibility** | Template-based | Fully customizable |
| **Performance** | Good | Excellent |
| **Customization** | Limited | Unlimited |
| **Deployment** | Simple | Standard web app |
| **UI Components** | Pre-built | Custom components |
| **Real-time Updates** | Built-in | Custom implementation |
| **Mobile Support** | Basic | Fully responsive |

## 📝 Development Tips

### Hot Reload

Changes to components and pages will hot-reload automatically in development mode.

### Type Safety

The project uses TypeScript. All data types are defined in `types/index.ts`.

### Debugging

Use browser DevTools:
- Network tab for API calls
- Console for logs
- React DevTools for component inspection

## 🐛 Troubleshooting

### "No data found" error

- Check that CSV file exists at `../KODE_FIX/KODE FIX/AnomalyDetected_Test.csv`
- Verify date range matches data in CSV

### Charts not rendering

- Ensure Recharts is installed: `npm install recharts`
- Check browser console for errors

### Slow performance

- Reduce dataset size with date range
- Increase playback speed
- Use production build (`npm run build && npm start`)

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## 📄 License

This project is part of the GUARD anomaly detection system.

## 🤝 Contributing

To add new features or fix bugs:

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📞 Support

For questions or issues, refer to the main GUARD system documentation.

---

**Built with ❤️ using Next.js 14, React 19, TailwindCSS, and Recharts**
