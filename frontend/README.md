# Custom HTS Frontend

React + TypeScript frontend for the Custom HTS application.

## Setup

Install dependencies:

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at http://localhost:5173

## Build

Build for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   │   ├── Navigation.tsx
│   │   └── StockCard.tsx
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx
│   │   ├── KoreanMarketPage.tsx
│   │   └── USMarketPage.tsx
│   ├── services/         # API service layer
│   │   ├── koreanMarket.ts
│   │   └── usMarket.ts
│   ├── types/            # TypeScript type definitions
│   │   ├── korean.ts
│   │   └── us.ts
│   ├── utils/            # Utility functions
│   │   └── format.ts
│   ├── App.tsx           # Main App component
│   ├── main.tsx          # Application entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript configuration
└── vite.config.ts        # Vite configuration
```

## Features

- **Korean Market Page**: Search and view Korean stocks with real-time quotes and financial statements
- **US Market Page**: Track US stocks with comprehensive financial data
- **Responsive Design**: Works on desktop and mobile devices
- **Type Safety**: Full TypeScript support with strict mode
- **Modern React**: Uses functional components and hooks
- **Fast Development**: Vite for instant hot module replacement

## Backend Integration

The frontend is configured to proxy API requests to the backend server running on port 8000. Make sure the backend is running before using the frontend.

## Technologies

- React 18
- TypeScript
- Vite
- React Router
- Axios
- Recharts (for future chart implementation)
