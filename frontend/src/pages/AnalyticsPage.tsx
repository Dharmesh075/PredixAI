import React from 'react';
import { AnalyticsResponse } from '../types';
import { 
  BarChart3, 
  Cpu, 
  CheckCircle2, 
  Award, 
  TrendingDown, 
  Zap, 
  FileCheck,
  ShieldCheck
} from 'lucide-react';

interface AnalyticsPageProps {
  analytics: AnalyticsResponse | null;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ analytics }) => {
  const benchmarks = analytics?.model_benchmarks || {};
  const clfModels = benchmarks.classification || {
    'SVM': { accuracy: 0.9600, precision: 0.8889, recall: 0.9600, f1_score: 0.9231, false_negative_rate: 0.0400 },
    'LightGBM': { accuracy: 0.9600, precision: 0.9200, recall: 0.9200, f1_score: 0.9200, false_negative_rate: 0.0800 },
    'XGBoost': { accuracy: 0.9500, precision: 0.9167, recall: 0.8800, f1_score: 0.8980, false_negative_rate: 0.1200 },
    'LSTM': { accuracy: 0.9500, precision: 0.9167, recall: 0.8800, f1_score: 0.8980, false_negative_rate: 0.1200 },
    'Random Forest': { accuracy: 0.9300, precision: 0.9091, recall: 0.8000, f1_score: 0.8511, false_negative_rate: 0.2000 }
  };

  const regModels = benchmarks.regression || {
    'XGBoost (Capped 125)': { mae: 10.74, rmse: 14.42, r2_score: 0.8796, nasa_total_score: 300.2, late_predictions_pct: 49.0 },
    'LightGBM': { mae: 11.29, rmse: 14.96, r2_score: 0.8705, nasa_total_score: 325.4, late_predictions_pct: 50.0 },
    'Random Forest': { mae: 11.48, rmse: 15.25, r2_score: 0.8653, nasa_total_score: 386.2, late_predictions_pct: 43.0 },
    'Kalman-LSTM (PyTorch)': { mae: 11.95, rmse: 16.32, r2_score: 0.8458, nasa_total_score: 382.9, late_predictions_pct: 60.0 },
    'XGBoost (Uncapped RUL)': { mae: 18.61, rmse: 26.03, r2_score: 0.6076, nasa_total_score: 6669.4, late_predictions_pct: 36.0 }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-black text-white flex items-center gap-2">
          Model Benchmarks & Prognostics Research
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono border border-emerald-500/30">
            Official C-MAPSS Evaluation
          </span>
        </h1>
        <p className="text-xs text-slate-400">
          Rigorous validation using Engine-Level Group Splitting (zero data leakage) and the NASA Asymmetric Penalty Metric
        </p>
      </div>

      {/* Benchmark 1: Failure Classification */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-400" />
              Failure Prediction Benchmark (Target: Failure &le; 30 Cycles)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Evaluated on 100 test engines at their last cycle. Key industrial metric: False Negative Rate (FNR).
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 font-semibold">
            Champion: SVM / LightGBM (F1: 0.923)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 font-mono text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3 pl-4">Model Architecture</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Precision</th>
                <th className="p-3">Recall</th>
                <th className="p-3">F1-Score</th>
                <th className="p-3 pr-4 text-emerald-400">FNR (Low = Safe)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {Object.entries(clfModels).map(([name, m]: any) => (
                <tr key={name} className="hover:bg-slate-800/40">
                  <td className="p-3 pl-4 font-bold text-white flex items-center gap-2">
                    {name === 'SVM' && <span className="text-amber-400 font-sans text-xs">🏆</span>}
                    {name}
                  </td>
                  <td className="p-3 text-slate-300">{(m.accuracy * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-300">{(m.precision * 100).toFixed(1)}%</td>
                  <td className="p-3 text-slate-300">{(m.recall * 100).toFixed(1)}%</td>
                  <td className="p-3 font-bold text-sky-400">{m.f1_score.toFixed(4)}</td>
                  <td className="p-3 pr-4 font-bold text-emerald-400">
                    {(m.false_negative_rate * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Benchmark 2: RUL Regression */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-sky-400" />
              Remaining Useful Life (RUL) Regression Benchmark
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Evaluated against ground truth (`truth_01.txt`). Compares piecewise linear capping ($RUL=125$) vs raw uncapped RUL.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold">
            Champion: XGBoost (RMSE: 14.42)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 font-mono text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3 pl-4">Model Architecture</th>
                <th className="p-3">MAE (Cycles)</th>
                <th className="p-3">RMSE (Cycles)</th>
                <th className="p-3">R² Score</th>
                <th className="p-3">NASA Score (Low = Best)</th>
                <th className="p-3 pr-4">Late Pred %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {Object.entries(regModels).map(([name, m]: any) => (
                <tr key={name} className="hover:bg-slate-800/40">
                  <td className="p-3 pl-4 font-bold text-white flex items-center gap-2">
                    {name.includes('XGBoost (Capped') && <span className="text-amber-400 font-sans text-xs">🏆</span>}
                    {name}
                  </td>
                  <td className="p-3 text-slate-300">{m.mae.toFixed(2)}</td>
                  <td className="p-3 font-bold text-sky-400">{m.rmse.toFixed(2)}</td>
                  <td className="p-3 text-slate-300">{m.r2_score.toFixed(4)}</td>
                  <td className={`p-3 font-bold ${m.nasa_total_score < 500 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {m.nasa_total_score.toFixed(1)}
                  </td>
                  <td className="p-3 pr-4 text-slate-400">{m.late_predictions_pct.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empirical Insight Note */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed">
          <strong className="text-sky-400 block mb-1 font-mono uppercase text-[11px]">
            Key Research Insight: Piecewise Linear Degradation Modeling
          </strong>
          Capping the RUL training target at 125 cycles prevents models from predicting large unconstrained numbers during early healthy cycles, reducing the asymmetric NASA exponential penalty from <strong className="text-red-400">6,669.4</strong> down to <strong className="text-emerald-400">300.2</strong> (a 95.5% penalty reduction) and lowering RMSE from 26.03 to 14.42 cycles.
        </div>
      </div>
    </div>
  );
};
