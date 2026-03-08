import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useState } from 'react';

export function ValuationWidget({ data, selectedAssets, loading }) {
    const [metric, setMetric] = useState('fwd_per'); // Default to Forward P/E

    const METRICS = [
        { id: 'fwd_per', label: 'FWD PER (전망)', color: '#3b82f6' },
        { id: 'ttm_per', label: 'PER (실적)', color: '#8b5cf6' },
        { id: 'pbr', label: 'PBR (자산)', color: '#10b981' },
        { id: 'psr', label: 'PSR (매출)', color: '#f59e0b' },
        { id: 'ev_ebitda', label: 'EV/EBITDA', color: '#ef4444' },
        { id: 'dividend_yield', label: '배당률 (%)', color: '#ec4899' },
        { id: 'roe', label: '수익성 (ROE %)', color: '#6366f1' },
    ];

    if (loading) {
        return (
            <div className="w-full h-80 flex items-center justify-center bg-white border rounded">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="w-full h-80 flex flex-col items-center justify-center bg-gray-50 border border-gray-200 border-dashed rounded text-gray-400">
                종목을 선택하면 밸류에이션 비교 데이터가 나타납니다.
            </div>
        );
    }

    // Filter out crypto or error responses
    const validData = data.filter(d => !d.error);

    if (validData.length === 0) {
        return (
            <div className="w-full p-6 text-center text-gray-500 bg-gray-50 border rounded">
                선택하신 종목(암호화폐 등)은 전통적인 재무 밸류에이션 지표가 존재하지 않습니다. 주식을 추가해주세요.
            </div>
        );
    }

    const activeMetricObj = METRICS.find(m => m.id === metric);

    return (
        <div className="w-full bg-white p-3 sm:p-4 border rounded shadow-sm">
            <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-4 sm:mb-6">
                {METRICS.map(m => (
                    <button
                        key={m.id}
                        onClick={() => setMetric(m.id)}
                        className={`px-2.5 py-1 sm:px-3 sm:py-1.5 text-xs sm:text-sm font-bold rounded-full transition-colors border ${metric === m.id
                                ? 'bg-blue-50 text-blue-600 border-blue-200 shadow-sm'
                                : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                            }`}
                    >
                        {m.label}
                    </button>
                ))}
            </div>

            <div className="h-[300px] sm:h-[400px]">
                <h4 className="font-bold text-gray-700 text-sm sm:text-base mb-2 relative pl-3">
                    <span className="absolute left-0 top-1 bottom-1 w-1 bg-blue-500 rounded"></span>
                    다중 {activeMetricObj.label} 비교
                </h4>
                <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={validData} layout="vertical" margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f3f4f6" />
                        <XAxis type="number" stroke="#9ca3af" tick={{ fontSize: 10 }} />
                        <YAxis dataKey="symbol" type="category" stroke="#4b5563" fontWeight="bold" tick={{ fontSize: 10 }} width={60} />
                        <Tooltip
                            cursor={{ fill: '#f9fafb' }}
                            contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontWeight: 'bold', fontSize: '12px' }}
                        />
                        <Bar
                            dataKey={metric}
                            fill={activeMetricObj.color}
                            radius={[0, 4, 4, 0]}
                            barSize={20}
                            name={activeMetricObj.label}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
