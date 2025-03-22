
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/api/auth/register`, {
        username,
        email,
        password,
      });
      localStorage.setItem("token", response.data.token);
      navigate("/login");
      alert("Signup successful! Please log in.");
    } catch (err) {
      setError(err.response?.data?.error || "Signup failed");
      alert("Signup failed");
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen">
      <form
        onSubmit={handleSignup}
        className="w-96 p-8 bg-transparent border border-white rounded-xl shadow-lg backdrop-blur-md text-white flex flex-col"
      >
        <h2 className="text-2xl font-semibold text-center mb-6">Sign Up</h2>
        {error && <p className="text-red-400 text-center">{error}</p>}

        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
          className="w-full p-3 rounded-md bg-transparent border border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition mb-4"
        />

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          className="w-full p-3 rounded-md bg-transparent border border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition mb-4"
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          className="w-full p-3 rounded-md bg-transparent border border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition mb-6"
        />

        <button
          type="submit"
          className="w-full py-3 bg-gradient-to-r from-green-500 to-teal-600 hover:from-teal-600 hover:to-green-500 text-white font-semibold rounded-md shadow-md transform hover:scale-105 transition duration-300"
        >
          Sign Up
        </button>

        <div className="mt-4 text-center">
          <p className="text-sm text-gray-400">
            Already have an account?{" "}
            <Link to="/login" className="text-green-400 hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Signup;
