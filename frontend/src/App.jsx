import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import heroImg from "./assets/hero.png";
import "./App.css";
import checkHealth from "./api/client";

function App() {
  const [status, setStatus] = useState("sprawdzam...");

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(JSON.stringify(data)))
      .catch((err) => setStatus(`błąd: ${err.message}`));
  }, []);

  return <div>Status backendu: {status}</div>;
}

export default App;
