import { Globe, RefreshCw } from 'lucide-react';

export function NewsFeedPanel({ news, loading }) {
    if (loading) {
        return (
            <div className="w-full bg-white border border-gray-200 rounded-lg p-6 shadow-sm animate-pulse mb-6">
                <div className="h-6 w-1/3 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-3">
                    <div className="h-4 bg-gray-100 rounded w-full"></div>
                    <div className="h-4 bg-gray-100 rounded w-5/6"></div>
                    <div className="h-4 bg-gray-100 rounded w-4/6"></div>
                </div>
            </div>
        );
    }

    if (!news || !news.ai_summary || !news.ai_summary.summary_points) {
        return null;
    }

    const points = news.ai_summary.summary_points;

    return (
        <div className="w-full bg-black text-white rounded-lg p-6 shadow-md mb-6 relative overflow-hidden">
            {/* Decorative accent */}
            <div className="absolute top-0 left-0 w-2 h-full bg-emerald-500"></div>

            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-black flex items-center gap-2">
                    <Globe className="text-emerald-400" />
                    Global Markets Briefing
                </h2>
                <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded font-bold border border-emerald-500/30">
                    AI SUMMARY
                </span>
            </div>

            <div className="space-y-3">
                {points.map((point, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></div>
                        <p className="text-gray-300 leading-relaxed text-sm md:text-base">
                            {point}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
