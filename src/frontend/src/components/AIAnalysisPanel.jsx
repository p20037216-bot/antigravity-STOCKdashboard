import { Activity, TrendingUp, TrendingDown, Minus, Cpu } from 'lucide-react';

export function AIAnalysisPanel({ data, error }) {
    if (error) {
        return (
            <div className="w-full bg-red-50 border border-red-200 text-red-700 p-6 rounded-lg flex items-center gap-3">
                <Cpu className="text-red-500" />
                <span>에러가 발생했습니다: {error}</span>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="w-full h-48 bg-gray-50 border border-gray-200 text-gray-400 p-6 rounded-lg flex items-center justify-center animate-pulse">
                <Cpu className="mr-2" />
                <span>AI가 5년치 데이터를 심층 분석 중입니다...</span>
            </div>
        );
    }

    const { ai_analysis, backtest_metrics, type, symbol } = data;

    // Format Opinion Icon & Color
    const opinion = ai_analysis.overall_opinion?.toLowerCase() || 'hold';
    const isBuy = opinion.includes('buy');
    const isSell = opinion.includes('sell');

    let OpinionIcon = Minus;
    let opinionColor = "text-gray-900 border-gray-900 bg-gray-100";

    if (isBuy) {
        OpinionIcon = TrendingUp;
        opinionColor = "text-emerald-500 border-emerald-500 bg-emerald-50";
    } else if (isSell) {
        OpinionIcon = TrendingDown;
        opinionColor = "text-red-500 border-red-500 bg-red-50";
    }

    return (
        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">

            {/* 백테스트 결과 패널 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-2 border-b border-gray-100 pb-3 mb-4">
                    <Activity className="text-black" size={20} />
                    <h3 className="text-lg font-bold text-black">5년 백테스트 레포트</h3>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm text-gray-500 mb-1">전략 승률 (Win Rate)</p>
                        <p className="text-2xl font-black text-black">
                            {Number(backtest_metrics.win_rate_pct).toFixed(1)}<span className="text-lg text-emerald-500 ml-1">%</span>
                        </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm text-gray-500 mb-1">누적 수익률 (Total Return)</p>
                        <p className={`text-2xl font-black ${backtest_metrics.total_return_pct >= 0 ? 'text-black' : 'text-red-500'}`}>
                            {backtest_metrics.total_return_pct >= 0 ? '+' : ''}
                            {Number(backtest_metrics.total_return_pct).toFixed(1)}<span className="text-lg text-gray-400 ml-1">%</span>
                        </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm text-gray-500 mb-1">총 매매 횟수 (Trades)</p>
                        <p className="text-xl font-bold text-black">{backtest_metrics.total_trades} 회</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-md">
                        <p className="text-sm text-gray-500 mb-1">최대 낙폭 (MDD)</p>
                        <p className="text-xl font-bold text-red-500">{Number(backtest_metrics.max_drawdown_pct || 0).toFixed(1)} %</p>
                    </div>
                </div>
                <p className="text-xs text-gray-400 mt-4">* 전략: 20/50/200 골든크로스 & RSI 보조지표</p>
            </div>

            {/* AI 리포트 패널 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
                    <div className="flex items-center gap-2">
                        <Cpu className="text-emerald-500" size={20} />
                        <h3 className="text-lg font-bold text-black">Gemini AI 투자 의견</h3>
                    </div>
                    <div className={`flex items-center gap-1 px-3 py-1 border rounded-full text-sm font-bold ${opinionColor}`}>
                        <OpinionIcon size={16} />
                        <span className="uppercase">{ai_analysis.overall_opinion}</span>
                    </div>
                </div>

                <div className="space-y-4">
                    <div>
                        <h4 className="text-sm font-bold text-emerald-600 mb-1 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> 상승 근거 (Buy Reason)
                        </h4>
                        <p className="text-sm text-gray-800 leading-relaxed bg-gray-50 p-3 rounded border-l-2 border-emerald-500">
                            {ai_analysis.buy_reason}
                        </p>
                    </div>

                    <div>
                        <h4 className="text-sm font-bold text-red-600 mb-1 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span> 하락 근거 (Sell Reason)
                        </h4>
                        <p className="text-sm text-gray-800 leading-relaxed bg-gray-50 p-3 rounded border-l-2 border-red-500">
                            {ai_analysis.sell_reason}
                        </p>
                    </div>
                </div>
            </div>

        </div>
    );
}
