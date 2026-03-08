import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export function SyncChart({ data, selectedAssets, loading }) {
    if (loading) {
        return (
            <div className="w-full h-96 flex flex-col items-center justify-center bg-white border rounded">
                <div className="w-10 h-10 border-4 border-gray-200 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500">동기화 차트 불러오는 중...</p>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="w-full h-96 flex flex-col items-center justify-center bg-gray-50 border border-gray-200 border-dashed rounded text-gray-400">
                위에서 종목과 기간을 선택해 차트를 동기화해주세요.
            </div>
        );
    }

    const colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white/90 p-3 shadow border rounded text-sm z-50">
                    <p className="font-bold border-b pb-1 mb-2">{label}</p>
                    <div className="space-y-1">
                        {payload.map((entry, index) => (
                            <div key={index} className="flex gap-4 justify-between" style={{ color: entry.color }}>
                                <span className="font-medium">{entry.name}:</span>
                                <span className="font-black">{(entry.value).toFixed(2)}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full h-[400px] sm:h-[500px] bg-white p-2 sm:p-4 border rounded">
            <h3 className="font-black text-base sm:text-lg mb-2 sm:mb-4 flex items-center gap-2 pl-2 sm:pl-0">
                📈 상대 수익률 비교 차트 (Sync-Compare)
            </h3>
            <ResponsiveContainer width="100%" height="85%">
                <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis
                        dataKey="date"
                        tick={{ fontSize: 10, fill: '#9ca3af' }}
                        minTickGap={30}
                        stroke="#9ca3af"
                        tickFormatter={(tick) => tick.substring(2)} // Shorten date for mobile
                    />
                    <YAxis
                        tickFormatter={(tick) => `${tick.toFixed(0)}%`}
                        tick={{ fontSize: 10, fill: '#9ca3af' }}
                        domain={['auto', 'auto']}
                        stroke="#9ca3af"
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />
                    {selectedAssets.map((asset, index) => (
                        <Line
                            key={asset.symbol}
                            type="monotone"
                            dataKey={asset.symbol}
                            stroke={colors[index % colors.length]}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                        />
                    ))}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
