const express = require("express");
const router = express.Router();
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const User = require("../models/User");
const authMiddleware = require("../middleware/auth");


router.post("/register", async (req, res) => {
  const { username, email, password } = req.body;

  try {

    let user = await User.findOne({ email });
    if (user) {
      return res.status(400).json({ error: "User already exists." });
    }

    // const salt = await bcrypt.genSalt(10);
    // const hashedPassword = await bcrypt.hash(password, salt);

    // user = new User({ username, email, password: hashedPassword });
    user = new User({ username, email, password }); // Save as plain text
    console.log("Raw Password:", password);
console.log("Hashed Password Before Saving:",password);

    await user.save();

    const token = jwt.sign({ id: user ._id }, process.env.JWT_SECRET, { expiresIn: "1h" });
    res.status(201).json({ token });
  } catch (err) {
    res.status(500).json({ error: "Server error." });
  }
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;
  console.log("Login attempt for:", email); 
  console.log("Entered Password:", password);
  
  try {
    const user = await User.findOne({ email });
    if (!user) {
      console.log("User not found");
      return res.status(400).json({ error: "Invalid credentials." });
    }

    // Directly compare plain text passwords
    if (password !== user.password) {  
      console.log("Password does not match");
      return res.status(400).json({ error: "Invalid credentials." });
    }

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "1h" });
    console.log("Token generated:", token); 
    res.json({ token });
  } catch (err) {
    console.error("Error during login:", err);
    res.status(500).json({ error: "Server error." });
  }
});




module.exports = router;