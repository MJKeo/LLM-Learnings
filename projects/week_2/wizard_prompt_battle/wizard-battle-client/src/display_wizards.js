import { useEffect, useState } from "react";

const STAT_CONFIG = [
  { key: "attack", label: "Attack", color: "#f87171" },
  { key: "defense", label: "Defense", color: "#60a5fa" },
  { key: "healing", label: "Healing", color: "#34d399" },
  { key: "arcane", label: "Arcane", color: "#c084fc" },
];

function DisplayWizards({ descriptions, apiBaseUrl, onReset, onBeginBattle = () => {} }) {
  const [results, setResults] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setResults([]);
      setErrorMessage("");

      const { playerOne, playerTwo } = descriptions;
      const entries = [
        { label: "Player 1", description: playerOne },
        { label: "Player 2", description: playerTwo },
      ];

      const appendResult = (label, updates) => {
        setResults((prev) => {
          const existing = prev.find((entry) => entry.label === label);
          if (existing) {
            return prev.map((entry) =>
              entry.label === label ? { ...entry, ...updates } : entry
            );
          }
          return [...prev, { label, ...updates }];
        });
      };

      try {
        await Promise.all(
          entries.map(async ({ label, description }) => {
            const statsResponse = await fetch(`${apiBaseUrl}/generate_wizard_stats`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ description }),
            });

            if (!statsResponse.ok) {
              throw new Error(`${label} wizard stats failed with status ${statsResponse.status}`);
            }

            const statsData = await statsResponse.json();
            appendResult(label, { stats: statsData, description });

            const spellsResponse = await fetch(`${apiBaseUrl}/generate_spells`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ description, stats: statsData }),
            });

            if (!spellsResponse.ok) {
              throw new Error(`${label} spell generation failed with status ${spellsResponse.status}`);
            }

            const spellsData = await spellsResponse.json();
            appendResult(label, { spells: spellsData });
          })
        );
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? `Failed to generate wizards or spells. ${error.message}`
            : "Failed to generate wizards or spells."
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [descriptions, apiBaseUrl]);

  const allComplete =
    results.length === 2 && results.every((entry) => entry.stats && entry.spells);

  return (
    <section className="wizard-section">
      {errorMessage && <p className="error-message">{errorMessage}</p>}

      {(!allComplete || isLoading) && (
        <div className="summary-header">
          <h2 className="summary-title">
            {isLoading && !allComplete ? "generating wizards..." : "Your wizards are ready for combat!"}
          </h2>
        </div>
      )}

      <div className="wizard-grid">
        {results.map(({ label, stats, spells }) => (
          <article key={label} className="wizard-card">
            <header className="wizard-header">
              <p className="wizard-label">{label}</p>
              {stats ? (
                <>
                  <h3 className="wizard-name">{stats.name}</h3>
                  <p className="wizard-style">{stats.combat_style}</p>
                  <div className="element-tags">
                    <span className={`element-pill element-${stats.primary_element.toLowerCase()}`}>
                      {stats.primary_element}
                    </span>
                    <span className={`element-pill element-${stats.secondary_element.toLowerCase()}`}>
                      {stats.secondary_element}
                    </span>
                  </div>
                </>
              ) : (
                <p className="loading-message">Awaiting stats...</p>
              )}
            </header>

            {stats && (
              <section className="wizard-stats">
                {STAT_CONFIG.map(({ key, label: statLabel, color }) => (
                  <div key={key} className="stat-row">
                    <span className="stat-label">{statLabel}</span>
                    <div className="stat-meter">
                      <div
                        className="stat-meter__fill"
                        style={{
                          width: `${Math.min(Math.max(stats[key], 0), 1) * 100}%`,
                          backgroundColor: color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </section>
            )}

            {spells && (
              <section className="wizard-spells">
                <h4 className="summary-subtitle">Spells</h4>
                <ul className="spell-list">
                  {spells.map((spell) => (
                    <li key={spell.name} className="spell-list__item">
                      {spell.name}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </article>
        ))}
      </div>

      <div className="wizard-footer-actions">
        <button className="prompt-button button-outline" type="button" onClick={onReset}>
          Start Over
        </button>
        {allComplete && (
          <button className="prompt-button" type="button" onClick={onBeginBattle}>
            Begin Battle
          </button>
        )}
      </div>
    </section>
  );
}

export default DisplayWizards;
