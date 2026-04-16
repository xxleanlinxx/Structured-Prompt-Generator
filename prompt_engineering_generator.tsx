import React, { useMemo, useState } from 'react';
import { Copy, Download, Plus, Trash2, RefreshCw, Sparkles, Languages } from 'lucide-react';

type Lang = 'en' | 'zh';
type ActionType = 'Search' | 'Lookup' | 'Browse';

type ActionItem = {
  type: ActionType;
  value: string;
};

type FormData = {
  domain: string;
  specialization: string;
  specificGoal: string;
  action: ActionItem[];
  details: string;
  constraints: string;
  format: string;
  structure: string;
  unwantedResult: string;
};

const DEFAULT_FORM: FormData = {
  domain: '',
  specialization: '',
  specificGoal: '',
  action: [{ type: 'Search', value: '' }],
  details: '',
  constraints: '',
  format: '',
  structure: '',
  unwantedResult: ''
};

const I18N = {
  en: {
    title: 'Structured Prompt Generator',
    subtitle: 'Design stronger prompts with quality feedback in real time.',
    score: 'Prompt Score',
    fill: 'Parameters',
    preview: 'Preview',
    insights: 'Insights',
    copy: 'Copy Prompt',
    copied: 'Copied!',
    download: 'Download .txt',
    reset: 'Reset',
    addAction: 'Add Action',
    remove: 'Remove',
    applyPreset: 'Apply Preset',
    selectPreset: 'Select preset',
    warnings: 'Warnings',
    suggestions: 'Suggestions',
    noSuggestions: 'Looks good. You can export now.',
    lang: '中文',
    fields: {
      domain: 'Domain',
      specialization: 'Specialization',
      specificGoal: 'Specific Goal',
      details: 'Context Details',
      constraints: 'Constraints',
      format: 'Output Format',
      structure: 'Structure',
      unwantedResult: 'Unwanted Result'
    },
    placeholders: {
      domain: 'e.g. product management, machine learning, digital marketing',
      specialization: 'e.g. growth strategy, LLM evaluation, B2B GTM',
      specificGoal: 'e.g. build a 90-day retention strategy for a subscription app',
      details: 'e.g. audience, budget, team size, current metrics',
      constraints: 'e.g. 8-week timeline, no paid ads, legal constraints',
      format: 'e.g. markdown, JSON, report',
      structure: 'e.g. {summary, analysis, recommendations, timeline}',
      unwantedResult: 'e.g. generic advice, no metrics, long paragraphs'
    },
    presets: {
      none: 'None',
      gtm: 'Startup GTM Plan',
      research: 'Research Synthesis',
      strategy: 'Product Strategy Brief'
    }
  },
  zh: {
    title: '結構化提示詞生成器',
    subtitle: '即時品質回饋，快速打造高品質提示詞。',
    score: '提示詞分數',
    fill: '參數設定',
    preview: '預覽',
    insights: '品質建議',
    copy: '複製 Prompt',
    copied: '已複製！',
    download: '下載 .txt',
    reset: '重置',
    addAction: '新增行動',
    remove: '刪除',
    applyPreset: '套用範本',
    selectPreset: '選擇範本',
    warnings: '警示',
    suggestions: '建議',
    noSuggestions: '內容很完整，可以直接匯出。',
    lang: 'English',
    fields: {
      domain: '領域',
      specialization: '專精項目',
      specificGoal: '具體目標',
      details: '背景細節',
      constraints: '限制條件',
      format: '輸出格式',
      structure: '結構',
      unwantedResult: '避免結果'
    },
    placeholders: {
      domain: '例如：產品管理、機器學習、數位行銷',
      specialization: '例如：成長策略、LLM 評估、B2B GTM',
      specificGoal: '例如：設計訂閱產品 90 天留存提升策略',
      details: '例如：受眾、預算、團隊規模、現況指標',
      constraints: '例如：8 週內完成、不能投放廣告、法規限制',
      format: '例如：markdown、JSON、報告',
      structure: '例如：{摘要, 分析, 建議, 時程}',
      unwantedResult: '例如：泛泛建議、沒有指標、段落過長'
    },
    presets: {
      none: '無',
      gtm: '新創成長策略',
      research: '研究整理簡報',
      strategy: '產品策略提案'
    }
  }
} as const;

const PRESETS: Record<Lang, Record<string, FormData>> = {
  en: {
    gtm: {
      ...DEFAULT_FORM,
      domain: 'growth marketing',
      specialization: 'B2B SaaS demand generation',
      specificGoal: 'build a 90-day GTM plan to grow qualified pipeline',
      action: [
        { type: 'Search', value: 'latest B2B SaaS demand generation benchmarks' },
        { type: 'Lookup', value: 'ICP segmentation framework' },
        { type: 'Browse', value: 'https://www.saastr.com' }
      ],
      details: 'Audience: US SMB teams. Budget: $40k/mo. Team: 4 marketers.',
      constraints: 'Keep CAC payback under 12 months.',
      format: 'markdown',
      structure: '{executive_summary, plan, KPI_dashboard, risks}',
      unwantedResult: 'generic advice without timeline'
    },
    research: {
      ...DEFAULT_FORM,
      domain: 'machine learning',
      specialization: 'LLM applications',
      specificGoal: 'summarize RAG advances and propose implementation options',
      action: [
        { type: 'Search', value: 'latest RAG papers and case studies' },
        { type: 'Lookup', value: 'reranker tradeoffs in production' }
      ],
      details: 'Audience: engineering managers. Knowledge base size: 20k docs.',
      constraints: 'Explain risks in plain language.',
      format: 'markdown',
      structure: '{overview, findings, options, recommendation}',
      unwantedResult: 'paper list without practical takeaway'
    },
    strategy: {
      ...DEFAULT_FORM,
      domain: 'product management',
      specialization: 'consumer subscriptions',
      specificGoal: 'design a retention strategy for D30 improvement',
      action: [
        { type: 'Search', value: 'subscription lifecycle messaging best practices' },
        { type: 'Lookup', value: 'cohort analysis interpretation for churn' }
      ],
      details: 'Current D30 retention is 18%. Category: wellness.',
      constraints: 'Prioritize low engineering effort experiments.',
      format: 'markdown',
      structure: '{problem, insights, experiments, measurement}',
      unwantedResult: 'recommendations without KPI'
    }
  },
  zh: {
    gtm: {
      ...DEFAULT_FORM,
      domain: '成長行銷',
      specialization: 'B2B SaaS 需求開發',
      specificGoal: '制定 90 天 GTM 計畫，提升高品質商機數量',
      action: [
        { type: 'Search', value: '2025 年 B2B SaaS demand generation benchmark' },
        { type: 'Lookup', value: 'ICP 分群與訊息矩陣框架' },
        { type: 'Browse', value: 'https://www.saastr.com' }
      ],
      details: '目標市場：美國 SMB。預算：每月 4 萬美元。',
      constraints: 'CAC 回收期需低於 12 個月。',
      format: 'markdown',
      structure: '{執行摘要, 計畫, KPI, 風險}',
      unwantedResult: '只有概念、沒有時程'
    },
    research: {
      ...DEFAULT_FORM,
      domain: '機器學習',
      specialization: 'LLM 應用',
      specificGoal: '整理 RAG 最新進展並提出導入方案',
      action: [
        { type: 'Search', value: '近期 RAG 論文與落地案例' },
        { type: 'Lookup', value: 'reranker 在實務上的取捨' }
      ],
      details: '受眾為工程經理，知識庫約 2 萬份文件。',
      constraints: '使用非研究人員也能理解的語言。',
      format: 'markdown',
      structure: '{背景, 洞察, 方案比較, 建議}',
      unwantedResult: '只列論文，不給執行建議'
    },
    strategy: {
      ...DEFAULT_FORM,
      domain: '產品管理',
      specialization: '訂閱制產品成長',
      specificGoal: '規劃提升留存的實驗路線圖',
      action: [
        { type: 'Search', value: 'subscription retention lifecycle best practices' },
        { type: 'Lookup', value: 'cohort churn 分析方法' }
      ],
      details: '目前 D30 留存 18%，品類為 wellness。',
      constraints: '優先低工程成本實驗。',
      format: 'markdown',
      structure: '{問題, 洞察, 實驗清單, 量測}',
      unwantedResult: '沒有 KPI 或責任人'
    }
  }
};

const ACTION_LABEL: Record<Lang, Record<ActionType, string>> = {
  en: { Search: 'Search', Lookup: 'Lookup', Browse: 'Browse' },
  zh: { Search: '搜尋', Lookup: '查找', Browse: '瀏覽' }
};

const escapeForPrompt = (value: string) => value.split('"').join('\\"').trim();

const generatePrompt = (data: FormData, lang: Lang) => {
  const actions = data.action.filter((item) => item.value.trim());
  const renderedActions = actions.length
    ? actions
        .map((item) => {
          const type = lang === 'zh' ? ACTION_LABEL.zh[item.type] : item.type;
          return `- [${type}("${escapeForPrompt(item.value)}")]`;
        })
        .join('\n')
    : lang === 'zh'
      ? '- [搜尋("{行動}")]'
      : '- [Search("{action}")]';

  if (lang === 'zh') {
    return `# <角色>
- 你是 ${data.domain || '{領域}'} 的專家，專精於 ${data.specialization || '{專精項目}'}。

# <任務>
- 你的任務是 ${data.specificGoal || '{具體目標}'}。

# <先推理再行動>
## 推理
- 讓我們一步一步思考。
## 行動
${renderedActions}
## 觀察
- 依據行動結果產出答案。

# <背景>
- 你需要的背景資訊：
  - ${data.details || '{背景細節}'}
  - ${data.constraints || '{限制條件}'}

# <輸出格式>
- 請以 ${data.format || '{輸出格式}'} 格式${data.structure ? `，並依照下列結構：${data.structure}。` : '，結構可自行決定。'}
- 請避免 ${data.unwantedResult || '{避免結果}'}。`;
  }

  return `# <Role>
- You are an expert in ${data.domain || '{domain}'} with specialization in ${data.specialization || '{specialization}'}.

# <Task>
- Your task is to ${data.specificGoal || '{specific goal}'}.

# <ReAct Framework: Reasoning & Action>
## Reasoning
- Let's think step by step.
## Action
${renderedActions}
## Observation
- Use the action results to produce the answer.

# <Context>
- Here is the context you need:
  - ${data.details || '{details}'}
  - ${data.constraints || '{constraints}'}

# <Output Format>
- Return a ${data.format || '{format}'} file${data.structure ? ` and follow this structure: ${data.structure}.` : ' (any structure is fine).'}
- Don't ${data.unwantedResult || '{unwanted result}'}.`;
};

const isValidUrl = (value: string) => {
  try {
    const url = new URL(value);
    return Boolean(url.protocol && url.hostname);
  } catch {
    return false;
  }
};

const getScore = (formData: FormData) => {
  const weights = {
    domain: 15,
    specialization: 10,
    specificGoal: 20,
    action: 25,
    details: 10,
    constraints: 10,
    format: 5,
    structure: 3,
    unwantedResult: 2
  } as const;

  let score = 0;
  if (formData.domain.trim()) score += weights.domain;
  if (formData.specialization.trim()) score += weights.specialization;
  if (formData.specificGoal.trim()) score += weights.specificGoal;
  if (formData.action.some((item) => item.value.trim())) score += weights.action;
  if (formData.details.trim()) score += weights.details;
  if (formData.constraints.trim()) score += weights.constraints;
  if (formData.format.trim()) score += weights.format;
  if (formData.structure.trim()) score += weights.structure;
  if (formData.unwantedResult.trim()) score += weights.unwantedResult;

  return score;
};

const PromptEngineeringGenerator = () => {
  const [lang, setLang] = useState<Lang>('en');
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM);
  const [copied, setCopied] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState('none');

  const t = I18N[lang];
  const prompt = useMemo(() => generatePrompt(formData, lang), [formData, lang]);
  const score = useMemo(() => getScore(formData), [formData]);

  const warnings = useMemo(() => {
    const list: string[] = [];
    if (formData.action.some((item) => item.type === 'Browse' && item.value.trim() && !isValidUrl(item.value.trim()))) {
      list.push(lang === 'zh' ? '瀏覽行動建議填入有效網址（包含 https://）。' : 'Browse actions should include a valid URL (with https://).');
    }
    return list;
  }, [formData.action, lang]);

  const suggestions = useMemo(() => {
    const list: string[] = [];
    if (!formData.domain.trim() || !formData.specificGoal.trim() || !formData.format.trim() || !formData.action.some((item) => item.value.trim())) {
      list.push(lang === 'zh' ? '先補齊必要欄位（領域、目標、行動、輸出格式）。' : 'Fill required fields first (Domain, Goal, Action, Format).');
    }
    if (!formData.constraints.trim()) {
      list.push(lang === 'zh' ? '建議補上至少一條限制條件。' : 'Add at least one constraint to reduce vague output.');
    }
    if (!formData.unwantedResult.trim()) {
      list.push(lang === 'zh' ? '建議補上「避免結果」，提升輸出穩定度。' : 'Define an unwanted result so the model knows what to avoid.');
    }
    return list;
  }, [formData, lang]);

  const updateField = (key: keyof Omit<FormData, 'action'>, value: string) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const updateAction = (index: number, patch: Partial<ActionItem>) => {
    setFormData((prev) => ({
      ...prev,
      action: prev.action.map((item, idx) => (idx === index ? { ...item, ...patch } : item))
    }));
  };

  const addAction = () => {
    setFormData((prev) => ({ ...prev, action: [...prev.action, { type: 'Search', value: '' }] }));
  };

  const removeAction = (index: number) => {
    setFormData((prev) => {
      if (prev.action.length === 1) return prev;
      return { ...prev, action: prev.action.filter((_, idx) => idx !== index) };
    });
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  const downloadPrompt = () => {
    const element = document.createElement('a');
    const file = new Blob([prompt], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `generated_prompt_${lang}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const applyPreset = () => {
    if (selectedPreset === 'none') return;
    setFormData(PRESETS[lang][selectedPreset]);
  };

  const resetForm = () => {
    setFormData(DEFAULT_FORM);
    setSelectedPreset('none');
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_10%,#e2f2ff_0%,#f8fafc_40%,#f1f5f9_100%)] p-5 md:p-8">
      <div className="mx-auto max-w-7xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-200/60">
        <header className="bg-[linear-gradient(115deg,#0f172a_0%,#0f766e_55%,#f59e0b_130%)] p-6 text-white md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h1 className="text-2xl font-black tracking-tight md:text-4xl">{t.title}</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-100 md:text-base">{t.subtitle}</p>
            </div>
            <button
              onClick={() => setLang((prev) => (prev === 'en' ? 'zh' : 'en'))}
              className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur hover:bg-white/25"
            >
              <Languages size={16} />
              {t.lang}
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-6 p-6 xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] xl:p-8">
          <section className="space-y-5">
            <div className="rounded-2xl border border-teal-100 bg-teal-50/60 p-4 md:p-5">
              <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.15em] text-teal-700">{t.fill}</p>
                  <div className="mt-1 text-3xl font-black text-teal-900">{score}%</div>
                  <p className="text-sm text-teal-800">{t.score}</p>
                </div>
                <div className="flex w-full flex-col gap-2 md:w-[360px]">
                  <select
                    value={selectedPreset}
                    onChange={(e) => setSelectedPreset(e.target.value)}
                    className="w-full rounded-xl border border-teal-200 bg-white px-3 py-2 text-sm text-slate-700"
                  >
                    <option value="none">{t.presets.none}</option>
                    <option value="gtm">{t.presets.gtm}</option>
                    <option value="research">{t.presets.research}</option>
                    <option value="strategy">{t.presets.strategy}</option>
                  </select>
                  <div className="flex gap-2">
                    <button
                      onClick={applyPreset}
                      className="flex-1 rounded-xl bg-teal-600 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-700"
                    >
                      {t.applyPreset}
                    </button>
                    <button
                      onClick={resetForm}
                      className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      <RefreshCw size={14} />
                      {t.reset}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-5 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 md:p-6">
              <div className="grid gap-4 md:grid-cols-2">
                {(['domain', 'specialization', 'specificGoal', 'details', 'constraints', 'format', 'structure', 'unwantedResult'] as const).map((field) => (
                  <label key={field} className="space-y-1.5">
                    <span className="text-sm font-semibold text-slate-700">{t.fields[field]}</span>
                    <textarea
                      value={formData[field]}
                      onChange={(e) => updateField(field, e.target.value)}
                      rows={3}
                      placeholder={t.placeholders[field]}
                      className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                    />
                  </label>
                ))}
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-700">Action</h3>
                  <button
                    onClick={addAction}
                    className="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-700"
                  >
                    <Plus size={12} />
                    {t.addAction}
                  </button>
                </div>

                <div className="space-y-3">
                  {formData.action.map((action, index) => (
                    <div key={`action-${index}`} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                      <div className="grid gap-2 md:grid-cols-[180px_minmax(0,1fr)_90px]">
                        <select
                          value={action.type}
                          onChange={(e) => updateAction(index, { type: e.target.value as ActionType })}
                          className="rounded-lg border border-slate-300 bg-white px-2 py-2 text-sm"
                        >
                          <option value="Search">{ACTION_LABEL[lang].Search}</option>
                          <option value="Lookup">{ACTION_LABEL[lang].Lookup}</option>
                          <option value="Browse">{ACTION_LABEL[lang].Browse}</option>
                        </select>
                        <input
                          value={action.value}
                          onChange={(e) => updateAction(index, { value: e.target.value })}
                          placeholder={action.type === 'Browse' ? 'https://...' : 'Describe this step...'}
                          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                        />
                        <button
                          onClick={() => removeAction(index)}
                          disabled={formData.action.length === 1}
                          className="inline-flex items-center justify-center gap-1 rounded-lg border border-rose-200 bg-rose-50 px-2 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          <Trash2 size={13} />
                          {t.remove}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <aside className="space-y-5">
            <div className="rounded-2xl border border-slate-200 bg-slate-900 p-4 text-white md:p-5">
              <div className="mb-3 flex items-center gap-2">
                <Sparkles size={16} />
                <h2 className="text-sm font-bold uppercase tracking-[0.12em]">{t.preview}</h2>
              </div>
              <pre className="max-h-[360px] overflow-y-auto whitespace-pre-wrap rounded-xl bg-black/25 p-3 text-xs text-slate-100">{prompt}</pre>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                <button
                  onClick={copyToClipboard}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-600"
                >
                  <Copy size={14} />
                  {copied ? t.copied : t.copy}
                </button>
                <button
                  onClick={downloadPrompt}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-500 px-3 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400"
                >
                  <Download size={14} />
                  {t.download}
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4 md:p-5">
              <h3 className="text-sm font-bold text-slate-800">{t.insights}</h3>
              <div className="mt-3 space-y-3">
                {warnings.length > 0 && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                    <p className="font-semibold">{t.warnings}</p>
                    <ul className="mt-1 list-disc space-y-1 pl-5">
                      {warnings.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {suggestions.length > 0 ? (
                  <div className="rounded-xl border border-cyan-200 bg-cyan-50 p-3 text-sm text-cyan-900">
                    <p className="font-semibold">{t.suggestions}</p>
                    <ul className="mt-1 list-disc space-y-1 pl-5">
                      {suggestions.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900">{t.noSuggestions}</div>
                )}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default PromptEngineeringGenerator;
