import { useState, useEffect } from 'react';
import { Search, Hash, BarChart3, TrendingUp, Globe, MessageSquare, X, Plus } from 'lucide-react';
import { SyncChart } from './components/SyncChart';
import { ValuationWidget } from './components/ValuationWidget';
import { MacroWidget } from './components/MacroWidget';
import { AIChatWidget } from './components/AIChatWidget';
import './index.css';

const MAX_ASSETS = 6;
const PRESETS = [
  { label: '🔥 빅테크', symbols: [{ symbol: 'AAPL', type: 'stock' }, { symbol: 'MSFT', type: 'stock' }, { symbol: 'GOOGL', type: 'stock' }, { symbol: 'NVDA', type: 'stock' }] },
  { label: '👑 최고배당주', symbols: [{ symbol: 'MO', type: 'stock' }, { symbol: 'T', type: 'stock' }, { symbol: 'VZ', type: 'stock' }, { symbol: 'O', type: 'stock' }] },
  { label: '🏦 한국금융', symbols: [{ symbol: '105560.KS', type: 'stock' }, { symbol: '055550.KS', type: 'stock' }, { symbol: '086790.KS', type: 'stock' }] },
  { label: '💰 암호화폐', symbols: [{ symbol: 'BTC', type: 'crypto' }, { symbol: 'ETH', type: 'crypto' }, { symbol: 'SOL', type: 'crypto' }, { symbol: 'XRP', type: 'crypto' }] },
];

function App() {
  const [activeTab, setActiveTab] = useState('chart'); // 'chart' | 'valuation' | 'macro' | 'chat'

  // Tag Selection State
  const [selectedAssets, setSelectedAssets] = useState([
    { symbol: 'AAPL', type: 'stock' },
    { symbol: 'NVDA', type: 'stock' }
  ]);
  const [searchInput, setSearchInput] = useState('');
  const [searchType, setSearchType] = useState('stock');

  // Chart State
  const [chartData, setChartData] = useState([]);
  const [loadingChart, setLoadingChart] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Trending Assets State
  const [popularAssets, setPopularAssets] = useState([]);

  // Valuation State
  const [valuationData, setValuationData] = useState([]);
  const [loadingValuation, setLoadingValuation] = useState(false);

  useEffect(() => {
    if (selectedAssets.length > 0) {
      fetchChartData();
      if (activeTab === 'valuation') {
        fetchValuationData();
      }
    } else {
      setChartData([]);
      setValuationData([]);
    }
  }, [selectedAssets, activeTab]);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

  useEffect(() => {
    // Fetch dynamic trending assets on load
    fetch(`${API_BASE}/api/trending`)
      .then(res => res.json())
      .then(data => {
        if (data.assets && data.assets.length > 0) {
          setPopularAssets(data.assets);
        }
      })
      .catch(err => console.error("Failed to fetch trending:", err));
  }, []);

  const fetchChartData = async () => {
    setLoadingChart(true);
    try {
      const payload = { symbols: selectedAssets };
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;

      const response = await fetch(`${API_BASE}/api/compare/chart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      setChartData(result.chart_data);
    } catch (err) {
      console.error("Failed to fetch sync charts:", err);
    } finally {
      setLoadingChart(false);
    }
  };

  const fetchValuationData = async () => {
    setLoadingValuation(true);
    try {
      const response = await fetch(`${API_BASE}/api/compare/valuation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols: selectedAssets })
      });
      const result = await response.json();
      setValuationData(result.valuations);
    } catch (err) {
      console.error("Failed to fetch valuations:", err);
    } finally {
      setLoadingValuation(false);
    }
  };

  const handleAddAsset = (e) => {
    e.preventDefault();
    const sym = searchInput.trim().toUpperCase();
    if (sym && selectedAssets.length < MAX_ASSETS) {
      if (!selectedAssets.some(a => a.symbol === sym)) {
        setSelectedAssets([...selectedAssets, { symbol: sym, type: searchType }]);
      }
      setSearchInput('');
    }
  };

  const handleRemoveAsset = (sym) => {
    setSelectedAssets(selectedAssets.filter(a => a.symbol !== sym));
  };

  const handleApplyPreset = (presetSymbols) => {
    setSelectedAssets(presetSymbols.slice(0, MAX_ASSETS));
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-gray-900 font-sans pb-12">
      {/* Search Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-black flex items-center gap-2 mb-6 tracking-tight">
            📊 차트뷰 <span className="text-sm font-medium text-gray-400">Sync-Compare Terminal V3</span>
          </h1>

          {/* Unified Search Input */}
          <div className="bg-gray-100/50 p-4 sm:p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="font-bold text-gray-800 flex flex-col sm:flex-row items-start sm:items-center gap-2 mb-4 text-sm sm:text-base">
              <span className="flex items-center gap-1"><Search size={18} /> 종목 검색</span>
              <span className="hidden sm:inline">·</span>
              <span className="text-gray-500 font-medium">수익률 차트 & 밸류에이션 동시 비교</span>
            </h2>

            <form onSubmit={handleAddAsset} className="flex flex-col sm:flex-row gap-2 w-full max-w-4xl relative">
              <div className="flex w-full sm:w-auto relative flex-1">
                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="absolute left-2 top-1/2 -translate-y-1/2 bg-transparent text-sm font-bold text-gray-500 border-none outline-none focus:ring-0 z-10"
                >
                  <option value="stock">US/KR Stock</option>
                  <option value="crypto">Crypto</option>
                </select>
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="회사명, 티커 입력 (예: Apple, BTC)"
                  className="w-full pl-[110px] sm:pl-[130px] pr-4 py-3 sm:py-4 rounded-lg border border-gray-300 bg-white font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none placeholder-gray-400 text-sm sm:text-base"
                />
              </div>
              <button
                type="submit"
                disabled={selectedAssets.length >= MAX_ASSETS}
                className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 sm:py-0 rounded-lg font-black transition-colors flex items-center justify-center min-w-[60px]"
              >
                <Plus size={20} className="sm:w-6 sm:h-6" />
              </button>
            </form>

            <div className="text-xs text-gray-400 mt-2 mb-4 pl-1">
              *회사명/티커 입력 후 + 버튼 또는 검색 결과 클릭 · 최대 6종목
            </div>

            {/* Tag Container */}
            <div className="flex flex-wrap gap-2">
              {selectedAssets.map((asset, i) => {
                const colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];
                return (
                  <div key={asset.symbol} className="flex items-center gap-1.5 bg-white border border-gray-200 px-3 py-1.5 rounded-full shadow-sm">
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: colors[i % colors.length] }}
                    ></span>
                    <span className="font-bold text-sm">{asset.symbol}</span>
                    <button onClick={() => handleRemoveAsset(asset.symbol)} className="text-gray-400 hover:text-red-500">
                      <X size={14} />
                    </button>
                  </div>
                )
              })}
            </div>

            {/* Presets */}
            <div className="mt-8 pt-4 border-t border-gray-200/60">
              <h3 className="text-sm font-bold text-gray-700 mb-3">⚡️ 빠른 테마 그룹 선택</h3>
              <div className="flex flex-wrap gap-2">
                {PRESETS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => handleApplyPreset(p.symbols)}
                    className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 text-gray-700 text-sm font-bold rounded-lg shadow-sm transition-colors"
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Popular Individual Assets (Dynamic) */}
            <div className="mt-6">
              <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center justify-between">
                <span>🔥 실시간 인기 개별 종목 추천 (On-Demand)</span>
                <span className="text-xs text-gray-400 font-normal">크롤러가 1시간마다 자동 갱신합니다.</span>
              </h3>
              <div className="flex flex-wrap gap-2">
                {popularAssets.length === 0 ? (
                  <span className="text-sm text-gray-500 italic">추천 종목을 불러오고 있습니다...</span>
                ) : (
                  popularAssets.map((asset, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        if (selectedAssets.length < MAX_ASSETS && !selectedAssets.some(a => a.symbol === asset.symbol)) {
                          setSelectedAssets([...selectedAssets, { symbol: asset.symbol, type: asset.type }]);
                        }
                      }}
                      className="px-3 py-1.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-600 text-xs font-medium rounded-full transition-colors flex items-center gap-1"
                    >
                      <Plus size={12} /> {asset.name} ({asset.symbol})
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 4-Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex border-b border-gray-200 overflow-x-auto hide-scrollbar">
          <button
            onClick={() => setActiveTab('chart')}
            className={`flex-1 py-3 sm:py-4 px-2 sm:px-0 text-center font-bold text-[13px] sm:text-base border-b-2 transition-colors flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2 min-w-[70px] whitespace-nowrap ${activeTab === 'chart' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <TrendingUp size={18} className="sm:w-5 sm:h-5" /> <span>차트 비교</span>
          </button>
          <button
            onClick={() => setActiveTab('valuation')}
            className={`flex-1 py-3 sm:py-4 px-2 sm:px-0 text-center font-bold text-[13px] sm:text-base border-b-2 transition-colors flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2 min-w-[70px] whitespace-nowrap ${activeTab === 'valuation' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <BarChart3 size={18} className="sm:w-5 sm:h-5" /> <span>밸류에이션</span>
          </button>
          <button
            onClick={() => setActiveTab('macro')}
            className={`flex-1 py-3 sm:py-4 px-2 sm:px-0 text-center font-bold text-[13px] sm:text-base border-b-2 transition-colors flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2 min-w-[70px] whitespace-nowrap ${activeTab === 'macro' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <Globe size={18} className="sm:w-5 sm:h-5" /> <span>경제 지표</span>
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-3 sm:py-4 px-2 sm:px-0 text-center font-bold text-[13px] sm:text-base border-b-2 transition-colors flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2 min-w-[70px] whitespace-nowrap ${activeTab === 'chat' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          >
            <MessageSquare size={18} className="sm:w-5 sm:h-5" /> <span>AI 질문</span>
          </button>
        </div>

        {/* Tab Content Area */}
        <div className="mt-6 sm:mt-8">
          {activeTab === 'chart' && (
            <div className="animate-in fade-in duration-500">
              <div className="mb-4 bg-white p-3 sm:p-4 border rounded shadow-sm flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
                <span className="font-bold text-gray-700 text-sm flex items-center gap-1"><TrendingUp size={16} /> 차트 기간:</span>
                <div className="flex items-center gap-2 w-full sm:w-auto">
                  <input
                    type="date"
                    value={startDate}
                    onChange={e => setStartDate(e.target.value)}
                    className="flex-1 sm:flex-none border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                  <span className="text-gray-400">~</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={e => setEndDate(e.target.value)}
                    className="flex-1 sm:flex-none border border-gray-300 rounded px-2 py-1.5 text-sm focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <button
                  onClick={fetchChartData}
                  className="w-full sm:w-auto sm:ml-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 sm:py-1.5 rounded font-bold text-sm transition-colors"
                >
                  조회
                </button>
              </div>
              <SyncChart data={chartData} selectedAssets={selectedAssets} loading={loadingChart} />
            </div>
          )}

          {activeTab === 'valuation' && (
            <div className="animate-in fade-in duration-500">
              <ValuationWidget data={valuationData} selectedAssets={selectedAssets} loading={loadingValuation} />
            </div>
          )}

          {activeTab === 'macro' && (
            <div className="animate-in fade-in duration-500">
              <MacroWidget />
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="animate-in fade-in duration-500">
              <AIChatWidget selectedAssets={selectedAssets} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
