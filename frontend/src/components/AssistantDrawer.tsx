import React, { useState } from 'react';
import { Bot, Send, X, Sparkles, User, AlertCircle, Wrench, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { Machine } from '../types';

interface AssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedMachine?: Machine;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  metrics?: any;
  action?: string;
  timestamp: string;
}

export const AssistantDrawer: React.FC<AssistantDrawerProps> = ({
  isOpen,
  onClose,
  selectedMachine
}) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'assistant',
      text: `Hello! I am your AI Predictive Maintenance Diagnostics Assistant. I have real-time access to the entire fleet's telemetry, SHAP explainability factors, failure predictions, and equipment manuals.\n\nAsk me about any machine (e.g., "Why is ENG-003 at high risk?", "What is the recommended maintenance for ENG-004?").`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  if (!isOpen) return null;

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.askAssistant(input, selectedMachine?.machine_id);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: res.response,
        metrics: res.key_metrics,
        action: res.recommended_action,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: `Error connecting to diagnostic intelligence engine: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-[440px] bg-[#0F172A] border-l border-slate-800 z-50 flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-500/20 flex items-center justify-center text-sky-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              AI Maintenance Assistant
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 font-mono">
                RAG + SHAP
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Contextual Telemetry Diagnostics</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Suggested Prompts */}
      <div className="p-3 bg-slate-900/40 border-b border-slate-800/80 flex gap-2 overflow-x-auto text-[11px]">
        <button
          onClick={() => setInput('Why is ENG-003 showing a critical failure risk?')}
          className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 whitespace-nowrap transition-colors border border-slate-700/60"
        >
          Diagnose ENG-003
        </button>
        <button
          onClick={() => setInput('What sensors are causing the failure alert on ENG-004?')}
          className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 whitespace-nowrap transition-colors border border-slate-700/60"
        >
          SHAP Root Cause
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div key={m.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="w-7 h-7 rounded-lg bg-sky-500/20 flex items-center justify-center text-sky-400 shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-sky-600 text-white rounded-br-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                }`}
              >
                <div className="whitespace-pre-wrap">{m.text}</div>

                {/* Key Metrics HUD Pill */}
                {m.metrics && (
                  <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-2 gap-2 text-[10px] font-mono">
                    <div className="bg-slate-950 p-2 rounded">
                      <span className="text-slate-400 block">HEALTH SCORE</span>
                      <span className="text-emerald-400 font-bold">{m.metrics.health_score}%</span>
                    </div>
                    <div className="bg-slate-950 p-2 rounded">
                      <span className="text-slate-400 block">PREDICTED RUL</span>
                      <span className="text-amber-400 font-bold">{m.metrics.predicted_rul} Cycles</span>
                    </div>
                  </div>
                )}

                <div className="text-[9px] text-slate-400 text-right mt-1.5 font-mono">
                  {m.timestamp}
                </div>
              </div>
              {isUser && (
                <div className="w-7 h-7 rounded-lg bg-slate-700 flex items-center justify-center text-slate-200 shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-sky-400 animate-pulse p-2">
            <Sparkles className="w-4 h-4" />
            <span>Analyzing machine telemetry & SHAP sensor attribution...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask diagnostics or type maintenance query..."
            className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2 rounded-xl bg-sky-500 text-white hover:bg-sky-400 disabled:opacity-40 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
