import { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, YAxis } from 'recharts';

export function MacroWidget() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

    useEffect(() => {
        fetch(`${API_BASE}/api/macro`)
            .then(res => res.json())
            .then(d => {
                setData(d);
                setLoading(false);
            })
            .catch(err => {
                console.error("Macro fetch error", err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="w-full h-80 flex flex-col items-center justify-center bg-white border rounded gap-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
                <div className="text-sm text-gray-500 font-medium animate-pulse">13개의 미국 거시경제 지표를 분석 중입니다...</div>
            </div>
        );
    }

    if (!data || !data.indicators) return null;

    let statusConfig = { icon: ShieldCheck, color: "text-emerald-500", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "안정" };
    if (data.status === 'warning') statusConfig = { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-50 text-amber-700 border-amber-200", label: "주의" };
    if (data.status === 'risk') statusConfig = { icon: AlertOctagon, color: "text-red-500", bg: "bg-red-50 text-red-700 border-red-200", label: "위험" };

    const StatusIcon = statusConfig.icon;

    const renderSparkline = (history, colorHex) => {
        if (!history || history.length === 0) return null;

        // Find min and max for the YAxis domain to accurately show trends
        const values = history.map(h => h.value);
        const min = Math.min(...values);
        const max = Math.max(...values);
        const domainPadding = (max - min) * 0.1;

        return (
            <div className="h-10 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id={`color-${colorHex.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={colorHex} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={colorHex} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <YAxis hide domain={[min - domainPadding, max + domainPadding]} />
                        <Area type="monotone" dataKey="value" stroke={colorHex} fillOpacity={1} fill={`url(#color-${colorHex.replace('#', '')})`} strokeWidth={2} isAnimationActive={false} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        );
    };

    return (
        <div className="w-full flex flex-col gap-4">
            {/* Top Section: AI Summary & Traffic Light */}
            <div className="bg-white p-4 sm:p-5 border rounded shadow-sm flex flex-col lg:flex-row gap-4">
                {/* Traffic Light */}
                <div className={`shrink-0 rounded-xl p-4 sm:p-6 border flex flex-col items-center justify-center lg:w-64 ${statusConfig.bg}`}>
                    <StatusIcon size={48} className={`mb-2 sm:mb-3 sm:w-16 sm:h-16 ${statusConfig.color}`} />
                    <h4 className="text-lg font-black mb-1">현재 시장: {statusConfig.label}</h4>
                    <div className="text-xs font-medium opacity-80 text-center">
                        거시경제 종합 시그널
                    </div>
                </div>

                {/* AI Summary */}
                <div className="bg-gray-800 text-white rounded-xl p-4 sm:p-5 flex-1 shadow-inner">
                    <div className="text-sm font-bold text-gray-300 mb-3 flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span> AI 종합 브리핑
                    </div>
                    <ul className="space-y-2 text-sm text-gray-200">
                        {data.ai_summary && data.ai_summary.map((line, i) => (
                            <li key={i} className="flex gap-2">
                                <span className="text-blue-400 mt-0.5">•</span>
                                <span className="leading-relaxed">{line}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* 13 Indicators Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
                {data.indicators.map((ind, i) => {
                    let colorConfig = { text: "text-gray-600", bg: "bg-gray-50", border: "border-gray-200", hex: "#6b7280", badge: "bg-gray-100 text-gray-600" };
                    if (ind.impact === 'positive') colorConfig = { text: "text-emerald-600", bg: "bg-emerald-50/50", border: "border-emerald-200", hex: "#10b981", badge: "bg-emerald-100 text-emerald-700" };
                    if (ind.impact === 'negative') colorConfig = { text: "text-red-500", bg: "bg-red-50/50", border: "border-red-200", hex: "#ef4444", badge: "bg-red-100 text-red-700" };

                    return (
                        <div key={ind.id} className={`bg-white border ${colorConfig.border} rounded-xl p-4 flex flex-col shadow-sm hover:shadow-md transition-shadow`}>
                            <div className="flex justify-between items-start mb-2">
                                <h5 className="font-bold text-[13px] text-gray-700 truncate pr-2" title={ind.name}>{ind.name}</h5>
                                <div className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex gap-1 items-center shrink-0 ${colorConfig.badge}`}>
                                    {ind.trend === 'up' ? <TrendingUp size={10} /> : ind.trend === 'down' ? <TrendingDown size={10} /> : <Minus size={10} />}
                                    {ind.impact === 'positive' ? '긍정' : ind.impact === 'negative' ? '부정' : '중립'}
                                </div>
                            </div>

                            <div className={`text-2xl font-black ${colorConfig.text}`}>
                                {ind.id === 'unemployment' || ind.id === 'breakeven' || ind.id.includes('spread') || ind.id.includes('10y') || ind.id === 'fed_funds' || ind.id === 'high_yield' ? `${ind.value}%` : ind.value.toLocaleString()}
                            </div>

                            {/* Sparkline Chart */}
                            {renderSparkline(ind.history, colorConfig.hex)}

                            {/* Description */}
                            <div className="mt-3 pt-3 border-t border-gray-100 text-[11px] text-gray-500 leading-snug line-clamp-2" title={ind.desc}>
                                {ind.desc}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
