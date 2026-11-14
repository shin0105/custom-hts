/**
 * Main App component with routing.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { KoreanMarketPage } from './pages/KoreanMarketPage';
import { USMarketPage } from './pages/USMarketPage';
import { AccountCheckPage } from './pages/AccountCheckPage';
import { BondMarketPage } from './pages/BondMarketPage';
import { DomesticFuturesOptionsPage } from './pages/DomesticFuturesOptionsPage';
import { BasisPage } from './pages/BasisPage';
import { MarketColorProvider } from './theme/MarketColorProvider';

export const App: React.FC = () => {
  return (
    <MarketColorProvider>
      <Router>
        <div style={{ minHeight: '100vh' }}>
          <Navigation />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/korean" element={<KoreanMarketPage />} />
            <Route path="/bonds" element={<BondMarketPage />} />
            <Route path="/futures-options" element={<DomesticFuturesOptionsPage />} />
            <Route path="/basis" element={<BasisPage />} />
            <Route path="/us" element={<USMarketPage />} />
            <Route path="/account-check" element={<AccountCheckPage />} />
          </Routes>
        </div>
      </Router>
    </MarketColorProvider>
  );
};
