import { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, createRoutesFromElements, Route, RouterProvider } from "react-router-dom";
import Layout from "./Layout";
import Profile from "./components/Profile";
import Home from "./components/Home";
import MetaMaskLogin from "./components/MetaMaskLogin";
import ProtectedRoute from "./components/ProtectedRoutes";

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in via MetaMask
    const storedWallet = localStorage.getItem("walletAddress");
    if (storedWallet) {
      setUser(storedWallet);
    }
  }, []);

  const router = createBrowserRouter(
    createRoutesFromElements(
      <Route path="/" element={<Layout />}>
        {/* Public MetaMask Login Route */}
        <Route path="/login" element={<MetaMaskLogin setUser={setUser} />} />

        {/* Protected Routes */}
        <Route index element={<ProtectedRoute user={user}><Home /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute user={user}><Profile /></ProtectedRoute>} />
      </Route>
    )
  );

  return <RouterProvider router={router} />;
};

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
