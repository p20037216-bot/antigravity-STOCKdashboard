import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function ChartWidget({ data, symbol }) {
    if (!data || data.length === 0) {
        return <div className="h-64 flex items-center justify-center text-gray-500 border border-black p-4 rounded-md">No chart data available for {symbol}</div>;
    }

    // Ensure dates are parsed correctly
    const formattedData = data.map(item => ({
        ...item,
        formattedDate: new Date(item.Date || item.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
    }));

    // Find min/max for better Y-axis scaling
    const closes = formattedData.map(d => d.close).filter(Boolean);
    const minVal = Math.min(...closes) * 0.95;
    const maxVal = Math.max(...closes) * 1.05;

    return (
        <div className="w-full h-80 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h3 className="text-lg font-bold mb-4">{symbol} 실시간 차트 (최근 100일)</h3>
            <ResponsiveContainer width="100%" height="85%">
                <LineChart data={formattedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                    <XAxis
                        dataKey="formattedDate"
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        tickMargin={10}
                        minTickGap={30}
                    />
                    <YAxis
                        domain={[minVal, maxVal]}
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        tickFormatter={(value) => `$${value.toFixed(0)}`}
                        width={60}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#000', color: '#fff', borderRadius: '8px', border: 'none' }}
                        itemStyle={{ color: '#10B981' }}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="close"
                        name="종가 (Close)"
                        stroke="#000000"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 6, fill: '#10B981' }}
                    />
                    {/* Moving Averages */}
                    <Line type="monotone" dataKey="SMA_20" name="20일선" stroke="#9ca3af" strokeWidth={1} dot={false} />
                    <Line type="monotone" dataKey="BBU_20_2.0" name="볼린저 상단" stroke="#10B981" strokeDasharray="5 5" strokeWidth={1} dot={false} />
                    <Line type="monotone" dataKey="BBL_20_2.0" name="볼린저 하단" stroke="#10B981" strokeDasharray="5 5" strokeWidth={1} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
