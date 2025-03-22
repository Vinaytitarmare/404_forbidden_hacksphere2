import React, { useState } from "react";
import { ethers } from "ethers";
import { useNavigate } from "react-router-dom";

const MetaMaskLogin = ({ setUser }) => {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const connectMetaMask = async () => {
    if (!window.ethereum) {
      setError("MetaMask is not installed!");
      return;
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      const walletAddress = accounts[0];

      // Save login state
      localStorage.setItem("walletAddress", walletAddress);
      setUser(walletAddress);

      navigate("/");
    } catch (err) {
      setError("Failed to connect MetaMask");
    }
  };

  return (
    <div className="text-white" style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Login with MetaMask</h2>
      <button onClick={connectMetaMask} style={{ padding: "10px", fontSize: "16px" }}>
        Connect MetaMask
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default MetaMaskLogin;
