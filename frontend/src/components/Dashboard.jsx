import React, { useState } from 'react';
import { 
  Activity, LayoutGrid, Wifi, AlertTriangle, LineChart, 
  FileText, Users, Wrench, Sparkles, LogOut, 
  Search, Bell, Settings, MoreVertical, Sun, Moon, ChevronDown
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, LabelList
} from 'recharts';

// --- MOCK DATA ---
const performanceData = [
  { time: '00', value: 95 }, { time: '04', value: 90 }, { time: '08', value: 65 },
  { time: '12', value: 60 }, { time: '16', value: 45 }, { time: '20', value: 60 }, { time: '24', value: 55 }
];

const distributionData = [
  { name: 'Oct', assembly: 40, fabrication: 30, packaging: 20 },
  { name: 'Nov', assembly: 20, fabrication: 15, packaging: 10 },
  { name: 'Dec', assembly: 45, fabrication: 35, packaging: 25 },
];

const energyData = [
  { name: 'Line 1', high: 80, low: 30 }, { name: 'Line 2', high: 75, low: 35 },
  { name: 'Packaging', high: 45, low: 40 }, { name: 'Fabrication', high: 45, low: 40 },
];

const recentAlerts = [
  { id: 1, title: 'Temperature Exceeded Th...', location: 'Welding Unit E-03', time: '2 min ago', type: 'critical' },
  { id: 2, title: 'High Vibration Detected', location: 'Conveyor Belt C-05', time: '15 min ago', type: 'warning' },
  { id: 3, title: 'Maintenance Scheduled', location: 'CNC Machine A-01', time: '2 min ago', type: 'info' },
];

const deviceStatus = [
  { id: 'CNC Machine A-01', location: 'Assembly Line 1', health: 96, temp: 42, state: 'good' },
  { id: 'Robotic Arm B-12', location: 'Assembly Line 2', health: 88, temp: 38, state: 'good' },
  { id: 'Welding Unit E-03', location: 'Assembly Line 1', health: 58, temp: 42, state: 'critical' },
];

const Dashboard = () => {
  // State Utama Tema: true = Dark Mode, false = Light Mode
  const [darkMode, setDarkMode] = useState(true);

  // Pemetaan Warna Tema Dinamis
  const theme = {
    bgMain: darkMode ? 'bg-[#030712]' : 'bg-slate-50',
    bgCard: darkMode ? 'bg-[#0B1120]' : 'bg-white',
    bgInner: darkMode ? 'bg-[#030712]' : 'bg-slate-50',
    border: darkMode ? 'border-slate-800/80' : 'border-slate-200',
    borderSubtle: darkMode ? 'border-slate-800/40' : 'border-slate-100',
    textTitle: darkMode ? 'text-white' : 'text-slate-900',
    textBody: darkMode ? 'text-slate-300' : 'text-slate-600',
    textMuted: darkMode ? 'text-slate-500' : 'text-slate-400',
    
    gridStroke: darkMode ? '#1e293b' : '#e2e8f0',
    axisStroke: darkMode ? '#64748b' : '#94a3b8',
    labelFill: darkMode ? '#64748b' : '#475569',
    tooltipBg: darkMode ? '#0f172a' : '#ffffff',
    tooltipBorder: darkMode ? '#1e293b' : '#e2e8f0'
  };

  return (
    <div className={`min-h-screen ${theme.bgMain} ${theme.textBody} font-sans flex overflow-hidden selection:bg-blue-500/30 transition-colors duration-300`}>
      
      {/* SIDEBAR */}
      <aside className={`w-64 ${theme.bgCard} border-r ${theme.border} flex flex-col justify-between hidden md:flex transition-colors duration-300 shrink-0`}>
        <div>
          <div className={`h-20 flex items-center px-6 border-b ${theme.borderSubtle}`}>
            <div className="flex items-center gap-3">
              <div className="p-1.5 bg-blue-500 rounded-lg">
                <Activity size={20} className="text-white" />
              </div>
              <div>
                <h1 className={`font-bold text-lg leading-tight ${theme.textTitle}`}>IndustryOS</h1>
                <p className={`text-xs ${theme.textMuted}`}>AI Monitoring</p>
              </div>
            </div>
          </div>
          
          <nav className="p-4 flex flex-col gap-1.5">
            <NavItem icon={<LayoutGrid size={18} />} label="Overview" active darkMode={darkMode} />
            <NavItem icon={<Wifi size={18} />} label="Devices" darkMode={darkMode} />
            <NavItem icon={<AlertTriangle size={18} />} label="Alerts" darkMode={darkMode} />
            <NavItem icon={<LineChart size={18} />} label="Analytics" darkMode={darkMode} />
            <NavItem icon={<FileText size={18} />} label="Reports" darkMode={darkMode} />
            <NavItem icon={<Users size={18} />} label="Team Management" darkMode={darkMode} />
            <NavItem icon={<Wrench size={18} />} label="Maintenance" darkMode={darkMode} />
            <NavItem icon={<Sparkles size={18} />} label="AI Insights" darkMode={darkMode} />
          </nav>
        </div>
        
        <div className={`p-4 border-t ${theme.borderSubtle}`}>
          <button className={`flex items-center gap-3 text-sm ${theme.textMuted} hover:text-blue-500 transition-colors px-4 py-2 w-full`}>
            <LogOut size={18} />
            Log Out
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* HEADER */}
        <header className="h-20 px-8 flex justify-between items-center shrink-0">
          <div>
            <h2 className={`text-xl font-semibold ${theme.textTitle}`}>Overview</h2>
            <p className={`text-sm ${theme.textMuted}`}>Welcome back, John</p>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="Search" 
                className={`${theme.bgCard} border ${theme.border} rounded-full py-2 pl-10 pr-4 text-sm ${theme.textTitle} focus:outline-none focus:border-blue-500/50 w-64 transition-colors duration-300`}
              />
            </div>
            
            <div className="flex items-center gap-4 text-slate-400">
              <button 
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-xl ${theme.bgCard} border ${theme.border} hover:text-blue-500 text-slate-400 transition-all duration-300 shadow-sm`}
                title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
              >
                {darkMode ? <Sun size={18} className="text-amber-400" /> : <Moon size={18} className="text-indigo-600" />}
              </button>

              <Bell size={20} className="hover:text-blue-500 cursor-pointer transition-colors" />
              <Settings size={20} className="hover:text-blue-500 cursor-pointer transition-colors" />
              <div className={`w-8 h-8 rounded-full ${theme.bgCard} border ${theme.border} overflow-hidden ml-2 cursor-pointer`}>
                 <img src="https://api.dicebear.com/7.x/notionists/svg?seed=John" alt="User" />
              </div>
            </div>
          </div>
        </header>

        {/* SCROLLABLE DASHBOARD AREA */}
        <div className="flex-1 overflow-y-auto p-8 pt-0">
          
          {/* 1. KPI CARDS ROW */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <KpiCard title="Active Devices" value="248" trend="+12%" icon={<Wifi size={16}/>} theme={theme} darkMode={darkMode} />
            <KpiCard title="System Uptime" value="99.8%" trend="+0.3%" icon={<Activity size={16}/>} theme={theme} darkMode={darkMode} />
            <KpiCard title="Energy Usage" value="1,847 kWh" trend="-8%" icon={<Activity size={16}/>} isNegative theme={theme} darkMode={darkMode} />
            <KpiCard title="Efficiency Score" value="94.2" trend="+5.1%" icon={<LineChart size={16}/>} theme={theme} darkMode={darkMode} />
          </div>

          {/* 2. MIDDLE ROW (Chart + Alerts) */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
            
            {/* System Performance Chart */}
            <div className={`${theme.bgCard} lg:col-span-3 border ${theme.border} rounded-2xl p-6 flex flex-col relative overflow-hidden transition-colors duration-300`}>
              {darkMode && <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 blur-3xl pointer-events-none"></div>}

              <div className="flex justify-between items-center mb-6 relative z-10">
                <h3 className={`text-lg font-medium ${theme.textTitle}`}>System Performance</h3>
              </div>

              <div className="flex-1 min-h-[240px] relative z-10">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorPerf" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={darkMode ? 0.3 : 0.15}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={theme.gridStroke} />
                    <XAxis dataKey="time" stroke={theme.axisStroke} fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke={theme.axisStroke} fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, color: darkMode ? '#e2e8f0' : '#0f172a' }} />
                    <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorPerf)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recent Alerts */}
            <div className={`${theme.bgCard} lg:col-span-1 border ${theme.border} rounded-2xl p-6 flex flex-col transition-colors duration-300`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className={`font-medium ${theme.textTitle}`}>Recent Alerts</h3>
                <span className="text-blue-500 text-sm cursor-pointer hover:text-blue-400">View All</span>
              </div>
              <div className="flex flex-col gap-4">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className={`flex gap-4 p-3 rounded-xl ${theme.bgInner} border ${theme.borderSubtle}`}>
                    <div className={`mt-1 h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                      alert.type === 'critical' ? 'bg-red-500/20 text-red-500' : 
                      alert.type === 'warning' ? 'bg-amber-500/20 text-amber-500' : 
                      'bg-blue-500/20 text-blue-500'
                    }`}>
                      <AlertTriangle size={14} />
                    </div>
                    <div>
                      <h4 className={`text-sm font-medium ${theme.textTitle}`}>{alert.title}</h4>
                      <p className={`text-xs ${theme.textMuted} mt-0.5`}>{alert.location}</p>
                      <p className="text-[10px] text-slate-400 mt-1">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 3. BOTTOM ROW */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Production Distribution */}
            <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-6 relative overflow-hidden transition-colors duration-300 flex flex-col`}>
              <div className="flex justify-between items-center mb-2">
                <h3 className={`font-medium text-sm ${theme.textTitle}`}>Production Distribution</h3>
                <span className={`text-xs ${theme.textMuted} ${theme.bgInner} px-2 py-1 rounded border ${theme.border} flex items-center gap-1 cursor-pointer`}>
                  Month <ChevronDown size={12} />
                </span>
              </div>
              
              {/* Custom Legend Sesuai Gambar Acuan */}
              <div className="flex flex-wrap gap-x-4 gap-y-2 mb-4 relative z-10">
                <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span><span className={`text-xs ${theme.textMuted}`}>Assembly Line <span className={theme.textTitle}>38%</span></span></div>
                <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#8b5cf6]"></span><span className={`text-xs ${theme.textMuted}`}>Fabrication <span className={theme.textTitle}>30%</span></span></div>
                <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#06b6d4]"></span><span className={`text-xs ${theme.textMuted}`}>Packaging <span className={theme.textTitle}>18%</span></span></div>
              </div>

              <div className="flex-1 min-h-[160px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distributionData} margin={{ top: 20, right: 0, left: -25, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={theme.gridStroke} />
                    <XAxis dataKey="name" stroke={theme.axisStroke} fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{fill: darkMode ? '#1e293b' : '#f1f5f9', opacity: 0.3}} contentStyle={{ backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder }}/>
                    <Bar dataKey="assembly" stackId="a" fill="#3b82f6" radius={[0, 0, 4, 4]} barSize={40} />
                    <Bar dataKey="fabrication" stackId="a" fill="#8b5cf6" />
                    <Bar dataKey="packaging" stackId="a" fill="#06b6d4" radius={[4, 4, 0, 0]}>
                      <LabelList dataKey="packaging" position="top" formatter={() => 'Total: 76%'} fill={theme.labelFill} fontSize={10} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Energy Consumption by Zone */}
            <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-6 transition-colors duration-300`}>
              <h3 className={`font-medium text-sm ${theme.textTitle} mb-4`}>Energy Consumption by Zone</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={energyData} margin={{ top: 10, right: 0, left: -25, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={theme.gridStroke} />
                    <XAxis dataKey="name" stroke={theme.axisStroke} fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke={theme.axisStroke} fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder }} />
                    <Area type="monotone" dataKey="high" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.8} />
                    <Area type="monotone" dataKey="low" stackId="2" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.8} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Device Status */}
            <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-6 transition-colors duration-300`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className={`font-medium text-sm ${theme.textTitle}`}>Device Status</h3>
                <span className="text-blue-500 text-xs cursor-pointer hover:text-blue-400">View All</span>
              </div>
              <div className="flex flex-col gap-5">
                {deviceStatus.map((dev, idx) => (
                  <div key={idx} className="flex justify-between items-center">
                    <div>
                      <h4 className={`text-sm font-medium ${theme.textTitle}`}>{dev.id}</h4>
                      <p className={`text-xs ${theme.textMuted}`}>{dev.location}</p>
                    </div>
                    <div className="flex gap-6 text-right">
                      <div>
                        <p className={`text-[10px] ${theme.textMuted} mb-0.5`}>Health</p>
                        <p className={`text-sm font-medium ${dev.state === 'critical' ? 'text-red-500' : 'text-emerald-500'}`}>
                          {dev.health}%
                        </p>
                      </div>
                      <div>
                        <p className={`text-[10px] ${theme.textMuted} mb-0.5`}>Temp</p>
                        <p className={`text-sm font-medium ${theme.textTitle}`}>{dev.temp}°C</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
};

// --- SUB-COMPONENTS ---

const NavItem = ({ icon, label, active, darkMode }) => (
  <a href="#" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
    active 
      ? 'bg-blue-600/10 text-blue-500 font-medium' 
      : darkMode 
        ? 'text-slate-400 hover:text-white hover:bg-slate-800/50' 
        : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
  }`}>
    {icon}
    <span className="text-sm">{label}</span>
  </a>
);

const KpiCard = ({ title, value, trend, icon, isNegative, theme, darkMode }) => (
  <div className={`${theme.bgCard} border ${theme.border} rounded-2xl p-5 flex flex-col justify-between group hover:border-blue-500/30 transition-all duration-300 shadow-sm relative overflow-hidden`}>
    
    {darkMode && (
      <div className="absolute top-1/2 -left-4 w-32 h-32 bg-blue-500/35 blur-2xl rounded-full pointer-events-none -translate-y-1/2"></div>
    )}

    <div className="flex justify-between items-start mb-4 relative z-10">
      <h3 className={`${theme.textMuted} text-sm font-medium flex items-center gap-2`}>
         {icon} <span className="ml-1">{title}</span>
      </h3>
      <button className="text-slate-400 hover:text-blue-500"><MoreVertical size={16} /></button>
    </div>
    <div className="relative z-10">
      <div className={`text-3xl font-semibold ${theme.textTitle} tracking-tight mb-2`}>{value}</div>
      <div className="flex items-center gap-2">
        <span className={`text-xs px-2 py-0.5 rounded flex items-center gap-1 font-medium ${
          isNegative ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'
        }`}>
          {trend}
        </span>
        <span className={`text-xs ${theme.textMuted}`}>vs last week</span>
      </div>
    </div>
  </div>
);

export default Dashboard;