import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';

export function AssetGrid({ overview, loading, onSelectAsset }) {
    if (loading) {
        return (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="h-32 bg-white border border-gray-200 rounded-lg p-4 animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                        <div className="h-6 bg-gray-100 rounded w-3/4 mt-4"></div>
                    </div>
                ))}
            </div>
        );
    }

    if (!overview || overview.length === 0) return null;

    return (
        <div className="mb-8">
            <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-black"></span>
                Market Overview
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {overview.map((asset) => {
                    const isBuy = asset.signal === 'BUY';
                    const isSell = asset.signal === 'SELL';

                    let SignalIcon = Minus;
                    let signalColor = "text-gray-600 bg-gray-100";
                    let borderStyle = "border-gray-200";

                    if (isBuy) {
                        SignalIcon = TrendingUp;
                        signalColor = "text-emerald-700 bg-emerald-100";
                        borderStyle = "border-emerald-300 shadow-sm shadow-emerald-100";
                    } else if (isSell) {
                        SignalIcon = TrendingDown;
                        signalColor = "text-red-700 bg-red-100";
                        borderStyle = "border-red-300 shadow-sm shadow-red-100";
                    }

                    return (
                        <div
                            key={asset.symbol}
                            onClick={() => onSelectAsset(asset.symbol, asset.type)}
                            className={`bg-white border rounded-lg p-4 cursor-pointer hover:-translate-y-1 transition-transform ${borderStyle}`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="font-black text-lg">{asset.symbol}</span>
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold flex items-center gap-1 ${signalColor}`}>
                                    <SignalIcon size={10} />
                                    {asset.signal}
                                </span>
                            </div>
                            <div className="text-sm font-medium text-gray-800 mb-2">
                                ${Number(asset.price).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                            </div>
                            <div className="flex justify-between text-xs text-gray-500 border-t pt-2">
                                <span>Win: {Number(asset.win_rate).toFixed(0)}%</span>
                                <span className={asset.total_return >= 0 ? 'text-emerald-500 font-bold' : 'text-red-500 font-bold'}>
                                    {asset.total_return > 0 && '+'}{Number(asset.total_return).toFixed(1)}%
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
