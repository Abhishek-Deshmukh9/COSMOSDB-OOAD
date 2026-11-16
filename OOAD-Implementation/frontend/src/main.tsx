import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import Navbar from "./app/components/Navbar";
import Home from "./app/pages/Home";
import Observatory from "./app/pages/Observatory";
import ComparePlanets from "./app/pages/ComparePlanets";
import PlanetDetail from "./app/pages/PlanetDetail";
import AddPlanet from "./app/pages/AddPlanet";
import Gallery from "./app/pages/Gallery";
import SystemView from "./app/pages/SystemView";
import Analytics from "./app/pages/Analytics";
import App from "./App";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Navbar />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/observatory" element={<Observatory />} />
      <Route path="/compare" element={<ComparePlanets />} />
      <Route path="/add-planet" element={<AddPlanet />} />
      <Route path="/planet/:id" element={<PlanetDetail />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/gallery" element={<Gallery />} />
      <Route path="/system/:id" element={<SystemView />} />
      <Route path="/table" element={<App />} />
    </Routes>
  </BrowserRouter>
);
