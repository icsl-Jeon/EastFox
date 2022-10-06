import React from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import CanvasPage from "./pages/CanvasPage";
import LandingPage from "./pages/LandingPage";
import { Provider } from "react-redux";
import store from "./store/store";

function App() {
  return (
    <Provider store={store}>
      <div className="App">
        <Router>
          <Routes>
            <Route path={"/"} element={<LandingPage />} />
            <Route path={"/canvas"} element={<CanvasPage />} />
          </Routes>
        </Router>
      </div>
    </Provider>
  );
}

export default App;
