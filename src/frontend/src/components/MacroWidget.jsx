import { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, Activity } from 'lucide-react';

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
            <div className="w-full h-80 flex items-center justify-center bg-white border rounded">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
            </div>
        );
    }

    if (!data) return null;

    let statusConfig = { icon: ShieldCheck, color: "text-emerald-500", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", label: "안정" };
    if (data.status === 'warning') statusConfig = { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-50 text-amber-700 border-amber-200", label: "주의" };
    if (data.status === 'risk') statusConfig = { icon: AlertOctagon, color: "text-red-500", bg: "bg-red-50 text-red-700 border-red-200", label: "위험" };

    const StatusIcon = statusConfig.icon;

    return (
        <div className="w-full bg-white p-4 sm:p-6 border rounded shadow-sm">
            <h3 className="font-black text-base sm:text-lg mb-4 sm:mb-6 flex items-center gap-2">
                <Activity className="text-blue-500 w-5 h-5 sm:w-6 sm:h-6" /> 거시경제 지표 및 시장 신호등
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
                {/* Left: Traffic Light Status */}
                <div className={`col-span-1 rounded-xl p-4 sm:p-6 border flex flex-col items-center justify-center ${statusConfig.bg}`}>
                    <StatusIcon size={56} className={`mb-3 sm:mb-4 sm:w-16 sm:h-16 ${statusConfig.color}`} />
                    <h4 className="text-lg sm:text-xl font-black mb-1">현재 시장: {statusConfig.label}</h4>
                    <div className="text-xs sm:text-sm font-medium opacity-80 mt-1 sm:mt-2 text-center">
                        연준(FRED) 금리차 및 순유동성 기반 평가
                    </div>
                </div>

                {/* Right: AI Summary & Metrics */}
                <div className="col-span-1 md:col-span-2 flex flex-col gap-3 sm:gap-4">
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                        <div className="bg-gray-50 border rounded-lg p-3 text-center flex sm:flex-col justify-between items-center sm:block">
                            <div className="text-xs text-gray-500 font-bold mb-0 sm:mb-1">장단기 금리차 (10y-2y)</div>
                            <div className={`text-lg sm:text-xl font-black ${data.yield_spread_10y2y < 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                                {data.yield_spread_10y2y}%
                            </div>
                        </div>
                        <div className="bg-gray-50 border rounded-lg p-3 text-center flex sm:flex-col justify-between items-center sm:block">
                            <div className="text-xs text-gray-500 font-bold mb-0 sm:mb-1">하이일드 스프레드</div>
                            <div className="text-lg sm:text-xl font-black text-gray-700">
                                {data.high_yield_spread}%
                            </div>
                        </div>
                        <div className="bg-gray-50 border rounded-lg p-3 text-center flex sm:flex-col justify-between items-center sm:block">
                            <div className="text-xs text-gray-500 font-bold mb-0 sm:mb-1">달러 순유동성 추세</div>
                            <div className="text-lg sm:text-xl font-black text-gray-700">
                                {data.liquidity > 0 ? '+' : ''}{data.liquidity}%
                            </div>
                        </div>
                    </div>

                    {/* AI Summary */}
                    <div className="bg-gray-800 text-white rounded-lg p-3 sm:p-4 flex-1">
                        <div className="text-xs font-bold text-gray-400 mb-2 sm:mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-blue-400"></span> AI 거시경제 브리핑
                        </div>
                        <ul className="space-y-1.5 sm:space-y-2 text-[13px] sm:text-sm text-gray-200">
                            {data.ai_summary.map((line, i) => (
                                <li key={i} className="flex gap-2">
                                    <span className="text-blue-400 mt-0.5">•</span>
                                    <span>{line}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
