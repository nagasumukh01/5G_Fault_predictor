import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity,
  Cpu,
  AlertTriangle,
  Radio,
  BarChart3,
  Sliders,
  ShieldCheck,
  Server,
  Zap
} from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        setIsBackendOnline(res.status === 'online');
      } catch (err) {
        setIsBackendOnline(false);
      }
    };
    checkHealth();
    const timer = setInterval(checkHealth, 8000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { name: 'Overview', path: '/', icon: Activity },
    { name: 'Monitoring', path: '/monitoring', icon: Radio },
    { name: 'AI Prediction', path: '/prediction', icon: Zap },
    { name: 'Anomaly Detection', path: '/anomalies', icon: ShieldCheck },
    { name: 'Alert Center', path: '/alerts', icon: AlertTriangle },
    { name: 'Model Evaluation', path: '/evaluation', icon: BarChart3 },
    { name: '5G Simulator', path: '/simulator', icon: Sliders },
    { name: 'System Health', path: '/health', icon: Server },
  ];

  return (
    <header className="sticky top-0 z-50 noc-panel border-b border-slate-800/80 bg-[#0c101a]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Team */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Radio className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-300 text-lg tracking-tight">
                  5G FAULT PREDICTOR
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  NOC v1.0
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-medium tracking-wide">
                Team Dynamites • Telecom AI Testbed
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`
                  }
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Real-time Status Badge */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendOnline === true
                    ? 'bg-emerald-400 animate-ping'
                    : isBackendOnline === false
                    ? 'bg-rose-500'
                    : 'bg-amber-400'
                }`}
              />
              <span className="text-slate-300 font-mono text-[11px]">
                {isBackendOnline === true
                  ? 'API LIVE'
                  : isBackendOnline === false
                  ? 'OFFLINE'
                  : 'CONNECTING'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation bar */}
      <div className="lg:hidden flex overflow-x-auto px-4 py-2 space-x-2 border-t border-slate-800 bg-[#0a0d14]/80">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `whitespace-nowrap px-3 py-1 rounded text-xs ${
                isActive ? 'bg-cyan-500 text-black font-semibold' : 'text-slate-400'
              }`
            }
          >
            {item.name}
          </NavLink>
        ))}
      </div>
    </header>
  );
};
