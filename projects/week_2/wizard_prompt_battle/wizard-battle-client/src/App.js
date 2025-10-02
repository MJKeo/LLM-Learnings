import { useState } from "react";
import "./App.css";

function App() {
  const [phase, setPhase] = useState("player1");
  const [playerOneDraft, setPlayerOneDraft] = useState("");
  const [playerTwoDraft, setPlayerTwoDraft] = useState("");
  const [playerOneSummary, setPlayerOneSummary] = useState("");
  const [playerTwoSummary, setPlayerTwoSummary] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handlePlayerOneSubmit = () => {
    if (!playerOneDraft.trim()) {
      setErrorMessage("Please enter a wizard description for Player 1.");
      return;
    }
    setErrorMessage("");
    setPlayerOneSummary(playerOneDraft.trim());
    setPhase("player2");
  };

  const handlePlayerTwoSubmit = async () => {
    if (!playerTwoDraft.trim()) {
      setErrorMessage("Please enter a wizard description for Player 2.");
      return;
    }

    setErrorMessage("");
    setIsSubmitting(true);

    const playerTwoClean = playerTwoDraft.trim();
    const payload = {
      playerOne: playerOneSummary,
      playerTwo: playerTwoClean,
    };

    try {
      const response = await fetch("http://localhost:5000/wizards", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      setPlayerTwoSummary(playerTwoClean);
      setPhase("summary");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? `Failed to submit wizard descriptions. ${error.message}`
          : "Failed to submit wizard descriptions."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app">
      <h1 className="title">Hello World</h1>

      {phase === "player1" && (
        <section className="prompt-card">
          <label htmlFor="player-one-prompt" className="prompt-label">
            Player 1 enter your wizard description
          </label>
          <textarea
            id="player-one-prompt"
            className="prompt-input"
            value={playerOneDraft}
            onChange={(event) => setPlayerOneDraft(event.target.value)}
            placeholder="Describe your wizard..."
          />
          <button className="prompt-button" onClick={handlePlayerOneSubmit}>
            Submit
          </button>
          {errorMessage && <p className="error-message">{errorMessage}</p>}
        </section>
      )}

      {phase === "player2" && (
        <section className="prompt-card">
          <label htmlFor="player-two-prompt" className="prompt-label">
            Player 2 enter your wizard description
          </label>
          <textarea
            id="player-two-prompt"
            className="prompt-input"
            value={playerTwoDraft}
            onChange={(event) => setPlayerTwoDraft(event.target.value)}
            placeholder="Describe your wizard..."
          />
          <button
            className="prompt-button"
            onClick={handlePlayerTwoSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
          {errorMessage && <p className="error-message">{errorMessage}</p>}
        </section>
      )}

      {phase === "summary" && (
        <section className="prompt-card">
          <h2 className="summary-title">Wizard Summaries</h2>
          <p className="summary-line">
            <span className="summary-label">Player 1:</span> {playerOneSummary}
          </p>
          <p className="summary-line">
            <span className="summary-label">Player 2:</span> {playerTwoSummary}
          </p>
        </section>
      )}
    </div>
  );
}

export default App;
