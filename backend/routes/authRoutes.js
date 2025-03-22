const express = require("express");
const router = express.Router();
const jwt = require("jsonwebtoken");
const User = require("../models/User");

// POST /api/auth/metamask-login
router.post("/metamask-login", async (req, res) => {
  const { walletAddress, username } = req.body;

  if (!walletAddress) {
    return res.status(400).json({ error: "Wallet address is required" });
  }

  try {
    let user = await User.findOne({ walletAddress });

    if (!user) {
      // If user does not exist, create a new one
      if (!username) {
        return res.status(400).json({ error: "Username is required for new users" });
      }

      user = new User({ username, walletAddress });
      await user.save();
    }

    // Generate JWT token
    const token = jwt.sign({ id: user._id, walletAddress: user.walletAddress }, process.env.JWT_SECRET, { expiresIn: "1h" });

    res.json({ token, message: "Login successful!" });
  } catch (err) {
    console.error("Error in MetaMask login:", err);
    res.status(500).json({ error: "Server error" });
  }
});

module.exports = router;
