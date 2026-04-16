# 🚀 Quick Start Guide - GUARD Dashboard

## ⚡ Run the Dashboard

### Option 1: Using the startup script (Recommended)
```bash
cd guard-dashboard
./run-dashboard.sh
```

### Option 2: Using npm directly
```bash
cd guard-dashboard
npm run dev
```

Then open **http://localhost:3000** in your browser.

## 🎯 What's Different from Streamlit?

| Aspect | Streamlit Version | Next.js/React Version |
|--------|------------------|---------------------|
| **UI Flexibility** | Fixed templates | Fully customizable |
| **Performance** | Good for prototypes | Production-ready |
| **Customization** | Limited by Streamlit | Complete control |
| **Deployment** | Streamlit Cloud | Any platform (Vercel, AWS, etc.) |
| **Responsive Design** | Basic | Fully responsive |
| **Component Library** | Built-in widgets | Custom React components |

## 📂 Project Structure

```
guard-dashboard/
├── app/
│   ├── page.tsx              # Main dashboard (START HERE!)
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles
│   └── api/data/route.ts     # API endpoint
│
├── components/               # All UI components
│   ├── StatsCard.tsx        # Metric cards
│   ├── ControlPanel.tsx     # Simulation controls
│   ├── MAEChart.tsx         # MAE timeline chart
│   ├── SensorChart.tsx      # Sensor readings chart
│   ├── AlertsPanel.tsx      # Anomaly alerts
│   └── Chatbot.tsx          # AI assistant
│
├── lib/
│   └── dataLoader.ts        # CSV data loading
│
└── types/
    └── index.ts             # TypeScript types
```

## 🎨 Customization Examples

### 1. Change Colors

Edit `tailwind.config.ts`:
```typescript
theme: {
  extend: {
    colors: {
      primary: '#YOUR_COLOR',    // Change primary blue
      danger: '#YOUR_COLOR',     // Change red/danger color
      // ... add more colors
    },
  },
},
```

### 2. Modify Chart Colors

Edit `components/MAEChart.tsx` or `components/SensorChart.tsx`:
```tsx
<Line stroke="#YOUR_COLOR" strokeWidth={3} />
```

### 3. Add New Stats Card

In `app/page.tsx`:
```tsx
<StatsCard
  title="Your Metric"
  value={yourValue}
  icon={<YourIcon />}
  color="primary"
/>
```

### 4. Customize Layout

Edit `app/page.tsx` - everything is in this file:
- Change grid layouts: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Adjust spacing: `gap-6`, `mb-8`, `py-8`
- Modify card styles in component files

### 5. Add New Features

Create new components in `components/`:
```tsx
// components/YourNewComponent.tsx
'use client';

export default function YourNewComponent() {
  return <div>Your content</div>;
}
```

Then import in `app/page.tsx`:
```tsx
import YourNewComponent from '@/components/YourNewComponent';
```

## 🛠️ Common Tasks

### Add a New Chart Type

1. Install additional chart library (if needed):
   ```bash
   npm install @recharts/additional-chart
   ```

2. Create component in `components/YourChart.tsx`

3. Import and use in `app/page.tsx`

### Change Date Range Default

Edit `app/page.tsx`:
```tsx
const [dateRange, setDateRange] = useState({
  startDate: '2025-XX-XX',  // Your start date
  endDate: '2025-XX-XX',    // Your end date
});
```

### Add Email Integration

1. Create `.env.local`:
   ```env
   SMTP_SERVER=your-smtp-server
   SMTP_PORT=587
   SMTP_USER=your-email
   SMTP_PASS=your-password
   ```

2. Create email API route in `app/api/email/route.ts`

3. Call from dashboard when anomaly detected

### Enable Real Email Alerts

Extend `app/page.tsx` in the `processNextDataPoint` function:
```tsx
if (currentData.status === 'ANOMALY') {
  // Send to your email API
  await fetch('/api/email/send', {
    method: 'POST',
    body: JSON.stringify({ anomalyData: currentData })
  });
}
```

## 📊 Data Flow

```
CSV File
   ↓
lib/dataLoader.ts (parse CSV)
   ↓
app/api/data/route.ts (API endpoint)
   ↓
app/page.tsx (fetch data)
   ↓
components/* (display data)
```

## 🔧 Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### CSS not updating
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### TypeScript errors
```bash
# Regenerate types
npm run dev  # This auto-generates types
```

### Data not loading
- Check CSV path in `lib/dataLoader.ts`
- Verify CSV exists at `../KODE_FIX/KODE FIX/AnomalyDetected_Test.csv`
- Check browser console for errors

## 📦 Dependencies

```json
{
  "next": "^16.2.4",           // Framework
  "react": "^19.2.5",          // UI library
  "tailwindcss": "^4.2.2",     // Styling
  "recharts": "^3.8.1",        // Charts
  "lucide-react": "^1.8.0",    // Icons
  "date-fns": "^4.1.0",        // Date formatting
  "typescript": "^6.0.2"       // Type safety
}
```

## 🚀 Production Deployment

### Build for Production
```bash
npm run build
npm start
```

### Deploy to Vercel (Free)
```bash
npm install -g vercel
vercel login
vercel
```

### Deploy to Other Platforms
- **Netlify**: Connect GitHub repo
- **AWS**: Use Amplify or Elastic Beanstalk
- **DigitalOcean**: App Platform
- **Docker**: See README.md for Dockerfile

## 🎓 Learning Resources

- **Next.js**: https://nextjs.org/docs
- **React**: https://react.dev/
- **TailwindCSS**: https://tailwindcss.com/docs
- **Recharts**: https://recharts.org/
- **TypeScript**: https://www.typescriptlang.org/docs

## 💡 Tips for Development

1. **Hot Reload**: Save any file to see changes instantly
2. **Component Isolation**: Test components individually
3. **TypeScript**: Use types for better IDE support
4. **Console**: Use `console.log()` to debug
5. **React DevTools**: Install browser extension

## 📝 Next Steps

1. ✅ Run the dashboard: `./run-dashboard.sh`
2. 🎨 Customize colors in `tailwind.config.ts`
3. 📊 Modify charts in `components/`
4. 🚀 Add new features as needed
5. 📱 Test on mobile devices
6. 🌐 Deploy to production

## 🤝 Support

For questions:
1. Check README.md for detailed documentation
2. Review component code in `components/`
3. Check Next.js documentation
4. Search Stack Overflow

---

**Happy coding! 🎉**
