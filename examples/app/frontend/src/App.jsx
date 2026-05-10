import { useState, useEffect } from "react";

const API = "http://localhost:8000";

const SENSITIVITY_COLOR = {
  health: "bg-red-100 text-red-800",
  sensitive_personal: "bg-orange-100 text-orange-800",
  personal: "bg-yellow-100 text-yellow-800",
  non_personal: "bg-gray-100 text-gray-600",
};

function Badge({ label, color }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {label}
    </span>
  );
}

function Section({ title, children }) {
  return (
    <div className="mb-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default function App() {
  const [activities, setActivities] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState("");
  const [dataSubjects, setDataSubjects] = useState("health_policyholders");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [vocabTab, setVocabTab] = useState("activities");

  useEffect(() => {
    fetch(`${API}/activities`)
      .then((r) => r.json())
      .then(setActivities)
      .catch(() => setError("Cannot reach API — is the backend running?"));

    fetch(`${API}/data-categories`)
      .then((r) => r.json())
      .then(setCategories)
      .catch(() => {});
  }, []);

  const activityDef = activities.find((a) => a.id === selectedActivity);

  async function handleGenerate() {
    if (!selectedActivity) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          activity: selectedActivity,
          data_subjects: dataSubjects.split(",").map((s) => s.trim()).filter(Boolean),
          // Omit data_used and legal_basis — let autofill kick in
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Generation failed");
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-7 h-7 rounded bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
            v
          </div>
          <div>
            <span className="font-semibold text-gray-900">vidhi-lang</span>
            <span className="ml-2 text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">
              v0.3 sample app
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-3 gap-6">
        {/* Left — Generator */}
        <div className="col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="font-semibold text-gray-900 mb-4">
              Generate RoPA entry
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">
                  Processing activity
                </label>
                <select
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  value={selectedActivity}
                  onChange={(e) => {
                    setSelectedActivity(e.target.value);
                    setResult(null);
                  }}
                >
                  <option value="">Select an activity…</option>
                  {activities.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name}
                    </option>
                  ))}
                </select>
                {activityDef && (
                  <p className="mt-1 text-xs text-gray-400">
                    {activityDef.description}
                  </p>
                )}
              </div>

              {activityDef && (
                <div className="rounded-lg bg-indigo-50 border border-indigo-100 p-3 text-xs space-y-1">
                  <p className="text-indigo-700 font-medium">
                    Autofill from taxonomy
                  </p>
                  <p className="text-indigo-600">
                    data_categories:{" "}
                    {activityDef.data_categories.join(", ") || "—"}
                  </p>
                  <p className="text-indigo-600">
                    legal_basis: {activityDef.legal_basis.join(", ") || "—"}
                  </p>
                  <p className="text-indigo-400 mt-1">
                    Omitted from request — generator will fill from activity
                    definition.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm text-gray-600 mb-1">
                  Data subjects{" "}
                  <span className="text-gray-400">(comma-separated)</span>
                </label>
                <input
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  value={dataSubjects}
                  onChange={(e) => setDataSubjects(e.target.value)}
                />
              </div>

              <button
                disabled={!selectedActivity || loading}
                onClick={handleGenerate}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              >
                {loading ? "Generating…" : "Generate RoPA entry"}
              </button>

              {error && (
                <p className="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}
            </div>
          </div>

          {/* Result */}
          {result && (
            <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
              <h2 className="font-semibold text-gray-900">RoPA entry</h2>

              <Section title="Activity">
                <code className="text-sm text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                  {result.activity}
                </code>
              </Section>

              <Section title="Data subjects">
                <div className="flex gap-2 flex-wrap">
                  {result.data_subjects.map((s) => (
                    <Badge key={s} label={s} color="bg-gray-100 text-gray-700" />
                  ))}
                </div>
              </Section>

              <Section title="Data categories">
                <div className="flex gap-2 flex-wrap">
                  {result.data_categories.map((c) => {
                    const cat = categories.find((x) => x.id === c);
                    const color =
                      SENSITIVITY_COLOR[cat?.sensitivity] ||
                      "bg-gray-100 text-gray-600";
                    return (
                      <Badge
                        key={c}
                        label={`${c}${cat ? ` (${cat.sensitivity})` : ""}`}
                        color={color}
                      />
                    );
                  })}
                </div>
              </Section>

              <Section title="Legal basis">
                <div className="flex gap-2 flex-wrap">
                  {result.legal_basis.map((l) => (
                    <Badge
                      key={l}
                      label={l}
                      color="bg-blue-100 text-blue-800"
                    />
                  ))}
                </div>
              </Section>

              <Section title="Obligations">
                <ul className="space-y-1">
                  {result.obligations.map((o) => (
                    <li key={o} className="flex items-center gap-2 text-sm">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 inline-block" />
                      <code className="text-gray-700">{o}</code>
                    </li>
                  ))}
                </ul>
              </Section>

              {result.potential_conflicts.length > 0 && (
                <Section title="Potential conflicts">
                  <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 space-y-1">
                    {result.potential_conflicts.map((c) => (
                      <div key={c} className="flex items-center gap-2">
                        <span className="text-amber-500">⚠</span>
                        <code className="text-sm text-amber-800">{c}</code>
                      </div>
                    ))}
                  </div>
                </Section>
              )}

              <Section title="Raw JSON">
                <pre className="text-xs bg-gray-50 rounded-lg p-3 overflow-auto border border-gray-100 max-h-48">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </Section>
            </div>
          )}
        </div>

        {/* Right — Vocabulary browser */}
        <div className="col-span-1">
          <div className="bg-white rounded-xl border border-gray-200 p-4 sticky top-6">
            <h2 className="font-semibold text-gray-900 mb-3 text-sm">
              Vocabulary
            </h2>

            <div className="flex gap-1 mb-3">
              {["activities", "categories"].map((t) => (
                <button
                  key={t}
                  onClick={() => setVocabTab(t)}
                  className={`text-xs px-2 py-1 rounded ${
                    vocabTab === t
                      ? "bg-indigo-100 text-indigo-700 font-medium"
                      : "text-gray-500 hover:bg-gray-50"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            {vocabTab === "activities" && (
              <div className="space-y-3">
                {activities.map((a) => (
                  <div key={a.id} className="text-xs">
                    <code className="text-indigo-600 block">{a.id}</code>
                    <span className="text-gray-500">{a.name}</span>
                  </div>
                ))}
              </div>
            )}

            {vocabTab === "categories" && (
              <div className="space-y-2">
                {categories.map((c) => (
                  <div key={c.id} className="text-xs">
                    <code className="text-indigo-600 block">{c.id}</code>
                    <Badge
                      label={c.sensitivity}
                      color={
                        SENSITIVITY_COLOR[c.sensitivity] ||
                        "bg-gray-100 text-gray-600"
                      }
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
