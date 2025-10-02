import { useState } from "react";
import "./App.css";
import GatherDescriptions from "./gather_descriptions";
import DisplayWizards from "./display_wizards";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ?? "http://localhost:3167";

function App() {
  const [descriptions, setDescriptions] = useState(null);

  const handleDescriptionsComplete = (playerOne, playerTwo) => {
    setDescriptions({ playerOne, playerTwo });
  };

  const handleReset = () => {
    setDescriptions(null);
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
        />
      )}
    </div>
  );
}

export default App;
