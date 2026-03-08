import { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

export function AIChatWidget({ selectedAssets }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: '안녕하세요! 현재 선택하신 종목들에 대해 어떤 투자 고민이 있으신가요? (예: 현재 금리 인상기인데 이 포트폴리오 괜찮을까?)' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || selectedAssets.length === 0) return;

        const userText = input;
        setMessages(prev => [...prev, { role: 'user', text: userText }]);
        setInput('');
        setLoading(true);

        const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

        try {
            const response = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbols: selectedAssets, question: userText })
            });
            const data = await response.json();
            setMessages(prev => [...prev, { role: 'assistant', text: data.answer }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', text: '오류가 발생했습니다. 백엔드 서버 상태를 확인해주세요.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full bg-white border rounded shadow-sm flex flex-col h-[450px] sm:h-[500px]">
            {/* Chat header */}
            <div className="bg-gray-50 px-3 sm:px-4 py-2.5 sm:py-3 border-b flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 sm:gap-0">
                <h3 className="font-bold flex items-center gap-2 text-sm sm:text-base">
                    <Bot className="text-blue-500 w-4 h-4 sm:w-5 sm:h-5" /> Gemini 종목 상담사
                </h3>
                <span className="text-[11px] sm:text-xs text-gray-500 font-medium truncate max-w-full">컨텍스트: {selectedAssets.map(a => a.symbol).join(', ') || '없음'}</span>
            </div>

            {/* Chat messages */}
            <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-2 sm:gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-gray-800 text-white' : 'bg-blue-100 text-blue-600'}`}>
                            {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                        </div>
                        <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-3 sm:px-4 py-2 ${msg.role === 'user' ? 'bg-blue-500 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none'}`}>
                            <p className="text-[13px] sm:text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-2 sm:gap-3">
                        <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center flex-shrink-0">
                            <Bot size={14} />
                        </div>
                        <div className="bg-gray-100 rounded-2xl rounded-tl-none px-3 sm:px-4 py-2 sm:py-3 flex gap-1 items-center">
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-gray-400 animate-bounce"></div>
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input area */}
            <form onSubmit={handleSend} className="p-2 sm:p-4 border-t bg-gray-50 flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="종목에 대해 파고들어 질문해 보세요..."
                    disabled={selectedAssets.length === 0}
                    className="flex-1 rounded-full border border-gray-300 px-3 sm:px-4 py-1.5 sm:py-2 text-[13px] sm:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200"
                />
                <button
                    type="submit"
                    disabled={loading || selectedAssets.length === 0}
                    className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex-shrink-0"
                >
                    <Send size={14} className="sm:w-4 sm:h-4" />
                </button>
            </form>
        </div>
    );
}
