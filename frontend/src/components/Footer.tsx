import React from 'react';
import { Shield, Radio, Terminal, Server } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-[#070a10] py-6 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-cyan-400" />
          <span className="text-slate-300 font-semibold">AI-Powered 5G Fault Prediction</span>
          <span>•</span>
          <span className="text-cyan-400 font-medium">Team Dynamites</span>
          <span>•</span>
          <span>Capstone Research Testbed</span>
        </div>

        <div className="flex items-center gap-6 font-mono text-[11px]">
          <span className="flex items-center gap-1 text-slate-400">
            <Server className="w-3.5 h-3.5 text-indigo-400" />
            FastAPI + SQLAlchemy
          </span>
          <span className="flex items-center gap-1 text-slate-400">
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            Random Forest + Isolation Forest
          </span>
          <span className="flex items-center gap-1 text-slate-400">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            Vercel & Render Ready
          </span>
        </div>
      </div>
    </footer>
  );
};
