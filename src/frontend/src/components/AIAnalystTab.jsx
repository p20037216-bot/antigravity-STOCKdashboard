import { useState, useEffect } from 'react';
import { Loader2, TrendingUp, TrendingDown, Minus, Play, BrainCircuit, Activity, BarChart3, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export function AIAnalystTab({ selectedAssets }) {
    const [analyzing, setAnalyzing] = useState(false);
    const [results, setResults] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

    // Automatically clear old results if selected assets change
    useEffect(() => {
        setResults(null);
        setErrorMsg('');
    }, [selectedAssets]);

    const handleAnalyze = async () => {
        if (!selectedAssets || selectedAssets.length === 0) return;
        setAnalyzing(true);
        setResults(null);
        setErrorMsg('');

        try {
            const payload = { symbols: selectedAssets };
            const response = await fetch(`${API_BASE}/api/analyze/analyst`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "AI 분석에 실패했습니다.");
            }

            setResults(data.analyses || []);
        } catch (err) {
            console.error(err);
            setErrorMsg(err.message);
        } finally {
            setAnalyzing(false);
        }
    };

    const getSignalBadge = (signalStr) => {
        const signal = signalStr ? signalStr.toLowerCase() : '';
        if (signal.includes('strong buy')) return { text: 'Strong Buy', bg: 'bg-emerald-100 text-emerald-800 border-emerald-300', icon: TrendingUp };
        if (signal.includes('buy')) return { text: 'Buy', bg: 'bg-green-100 text-green-700 border-green-200', icon: TrendingUp };
        if (signal.includes('strong sell')) return { text: 'Strong Sell', bg: 'bg-rose-100 text-rose-800 border-rose-300', icon: TrendingDown };
        if (signal.includes('sell')) return { text: 'Sell', bg: 'bg-red-100 text-red-700 border-red-200', icon: TrendingDown };
        return { text: 'Hold', bg: 'bg-amber-100 text-amber-700 border-amber-200', icon: Minus }; // Hold / Neutral
    };

    if (selectedAssets.length === 0) {
        return (
            <div className="bg-white p-8 rounded-xl border border-gray-200 text-center text-gray-500 shadow-sm">
                상단에서 분석할 종목(최대 6개)을 먼저 선택해주세요.
            </div>
        );
    }

    return (
        <div className="w-full">
            {/* Intro Header */}
            {!results && !analyzing && (
                <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 p-6 sm:p-10 rounded-2xl shadow-sm text-center mb-6 max-w-3xl mx-auto flex flex-col items-center gap-4">
                    <div className="bg-white p-4 rounded-full shadow-sm">
                        <BrainCircuit size={48} className="text-indigo-600" />
                    </div>
                    <h2 className="text-2xl font-black text-gray-800">월스트리트 AI 수석 애널리스트</h2>
                    <p className="text-gray-600 leading-relaxed text-sm sm:text-base max-w-xl">
                        현재 선택된 {selectedAssets.length}개 종목의 기술적 지표(이동평균선 등)와 기본적 지표(PER, PBR 등)를 실시간으로 종합하여 다각도로 분석하고 <b>명확한 매수/매도 의견</b>을 즉석에서 제공합니다.
                    </p>
                    <button
                        onClick={handleAnalyze}
                        className="mt-4 px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-lg shadow-md transition-all active:scale-95 flex items-center gap-2"
                    >
                        <Play size={18} fill="currentColor" /> 분석 시작하기
                    </button>
                </div>
            )}

            {/* Loading Skeleton Terminal */}
            {analyzing && (
                <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 shadow-xl w-full max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[300px]">
                    <Loader2 size={40} className="text-blue-500 animate-spin mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">실시간 데이터 수집 및 분석 중...</h3>
                    <div className="font-mono text-xs text-green-400 space-y-1 w-full max-w-md text-center opacity-80 mt-4 leading-relaxed">
                        <p className="animate-pulse">&gt; Fetching market prices and indicators...</p>
                        <p className="animate-pulse" style={{ animationDelay: '0.5s' }}>&gt; Computing P/E, P/B, and momentum...</p>
                        <p className="animate-pulse" style={{ animationDelay: '1s' }}>&gt; Connecting to Gemini Flash Model...</p>
                        <p className="animate-pulse" style={{ animationDelay: '1.5s' }}>&gt; Writing analyst intelligence report...</p>
                    </div>
                    <p className="text-slate-400 text-sm mt-8 border-t border-slate-700 pt-4 max-w-xs text-center">종목 수량에 따라 최대 10초~15초 소요될 수 있습니다.</p>
                </div>
            )}

            {/* Error Message */}
            {errorMsg && (
                <div className="bg-red-50 text-red-600 p-4 border border-red-200 rounded-xl flex items-center gap-3 mb-6">
                    <AlertTriangle size={20} className="shrink-0" />
                    <p className="font-medium text-sm">{errorMsg}</p>
                </div>
            )}

            {/* Results Grid */}
            {results && results.length > 0 && (
                <div className="flex flex-col gap-6">
                    <div className="flex justify-between items-end mb-2 px-2">
                        <h3 className="text-lg font-black text-gray-800 flex items-center gap-2">
                            <BrainCircuit size={20} className="text-indigo-600" /> 종합 애널리스트 리포트
                        </h3>
                        <button
                            onClick={handleAnalyze}
                            className="text-xs font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-3 py-1.5 rounded-full"
                        >
                            차트 갱신 & 재분석
                        </button>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        {results.map((res, i) => {
                            const signal = getSignalBadge(res.signal);
                            const SignalIcon = signal.icon;
                            return (
                                <div key={i} className="bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow flex flex-col overflow-hidden">

                                    {/* Card Header */}
                                    <div className="p-4 sm:p-5 border-b border-gray-100 flex justify-between items-start bg-gray-50/50">
                                        <div>
                                            <h4 className="text-xl sm:text-2xl font-black text-gray-800 flex items-center gap-2">
                                                {res.symbol}
                                            </h4>
                                            <div className="text-xs font-bold text-gray-500 mt-1.5 line-clamp-1">{res.company_name || "Name Unknown"}</div>
                                        </div>

                                        {/* Signal Badge */}
                                        <div className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-black text-sm shadow-sm ${signal.bg}`}>
                                            <SignalIcon size={16} />
                                            {signal.text}
                                        </div>
                                    </div>

                                    {/* Body Content */}
                                    <div className="p-4 sm:p-5 flex-1 flex flex-col gap-5">

                                        {/* Technical (Chart) */}
                                        <div>
                                            <h5 className="text-xs font-black text-blue-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                                <Activity size={12} /> 기술적 분석
                                            </h5>
                                            <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-xl border border-gray-100 leading-relaxed prose prose-sm max-w-none">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{res.technical_analysis}</ReactMarkdown>
                                            </div>
                                        </div>

                                        {/* Fundamental (Value) */}
                                        <div>
                                            <h5 className="text-xs font-black text-purple-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                                <BarChart3 size={12} /> 기본적 분석
                                            </h5>
                                            <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-xl border border-gray-100 leading-relaxed prose prose-sm max-w-none">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{res.fundamental_analysis}</ReactMarkdown>
                                            </div>
                                        </div>

                                        {/* Summary */}
                                        <div className="mt-auto border-t border-gray-100 pt-4">
                                            <h5 className="text-xs font-bold text-gray-400 mb-1">AI 총평</h5>
                                            <p className="text-sm font-bold text-gray-800 italic pr-2">
                                                "{res.summary}"
                                            </p>
                                        </div>

                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
