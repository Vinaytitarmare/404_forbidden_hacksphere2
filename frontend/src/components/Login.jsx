import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Web3 from "web3";

const Login = () => {
  const [walletAddress, setWalletAddress] = useState(localStorage.getItem("walletAddress") || "");
  const navigate = useNavigate();

  useEffect(() => {
    if (walletAddress) {
      localStorage.setItem("walletAddress", walletAddress);
      navigate("/"); // Redirect to home/dashboard after login
    }
  }, [walletAddress, navigate]);

  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        const web3 = new Web3(window.ethereum);
        await window.ethereum.request({ method: "eth_requestAccounts" });
        const accounts = await web3.eth.getAccounts();
        setWalletAddress(accounts[0]);
        localStorage.setItem("walletAddress", accounts[0]); // Save wallet address in localStorage
      } catch (error) {
        console.error("MetaMask connection error:", error);
      }
    } else {
      alert("MetaMask is not installed. Please install MetaMask to continue.");
    }
  };

  return (
    <div className="text-white" style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Login with MetaMask</h2>
      {walletAddress ? (
        <p>Connected as: {walletAddress}</p>
      ) : (
        <button onClick={connectWallet} style={{ padding: "10px 20px", fontSize: "16px", cursor: "pointer" }}>
          Connect to MetaMask
        </button>
      )}
    </div>
  );
};

export default Login;
