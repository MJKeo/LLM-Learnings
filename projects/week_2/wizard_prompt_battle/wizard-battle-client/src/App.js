import { useEffect, useState } from "react";
import "./App.css";
import GatherDescriptions from "./gather_descriptions";
import DisplayWizards from "./display_wizards";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ?? "http://localhost:3167";

function App() {
  const [descriptions, setDescriptions] = useState(null);
  const [playerOneWizard, setPlayerOneWizard] = useState(null);
  const [playerTwoWizard, setPlayerTwoWizard] = useState(null);

  useEffect(() => {
    setPlayerOneWizard(null);
    setPlayerTwoWizard(null);
  }, []);

  const handleDescriptionsComplete = (playerOne, playerTwo) => {
    setDescriptions({ playerOne, playerTwo });
  };

  const handleReset = () => {
    setDescriptions(null);
    setPlayerOneWizard(null);
    setPlayerTwoWizard(null);
  };

  const handleWizardReady = (label, wizardInstance) => {
    if (label === "Player 1") {
      setPlayerOneWizard(wizardInstance);
    } else if (label === "Player 2") {
      setPlayerTwoWizard(wizardInstance);
    }
  };

  return (
    <div className="app">
      {!descriptions ? (
        <GatherDescriptions onComplete={handleDescriptionsComplete} />
      ) : (
        <DisplayWizards
          descriptions={descriptions}
          apiBaseUrl={API_BASE_URL}
          onReset={handleReset}
          onBeginBattle={() => {
            /* TODO: hook into game flow */
          }}
          playerOneWizard={playerOneWizard}
          playerTwoWizard={playerTwoWizard}
          onWizardReady={handleWizardReady}
        />
      )}
    </div>
  );
}

export default App;
