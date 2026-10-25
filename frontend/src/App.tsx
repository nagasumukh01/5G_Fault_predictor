import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { NetworkMonitoring } from './pages/NetworkMonitoring';
import { FaultPrediction } from './pages/FaultPrediction';
import { AnomalyDetection } from './pages/AnomalyDetection';
import { AlertCenter } from './pages/AlertCenter';
import { ModelEvaluation } from './pages/ModelEvaluation';
import { SimulatorControls } from './pages/SimulatorControls';
import { SystemHealth } from './pages/SystemHealth';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0a0d14] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
        {/* Navigation Bar */}
        <Navbar />

        {/* Main View Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<ExecutiveOverview />} />
            <Route path="/monitoring" element={<NetworkMonitoring />} />
            <Route path="/prediction" element={<FaultPrediction />} />
            <Route path="/anomalies" element={<AnomalyDetection />} />
            <Route path="/alerts" element={<AlertCenter />} />
            <Route path="/evaluation" element={<ModelEvaluation />} />
            <Route path="/simulator" element={<SimulatorControls />} />
            <Route path="/health" element={<SystemHealth />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
