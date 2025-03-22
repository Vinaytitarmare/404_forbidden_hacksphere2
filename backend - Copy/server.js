require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const path = require("path");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const app = express();
app.use(cors());
app.use(express.json());
// require("./biddingScheduler");

const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.MONGO_URI, {
    dbName: "auctionDB",
  })
  .then(() => console.log("MongoDB Connected ✅"))
  .catch((err) => console.error("MongoDB Connection Error:", err));

const User= require("./models/User")
const JWT_SECRET = process.env.JWT_SECRET || "your_jwt_secret";


const authenticateUser = (req, res, next) => {
  const token = req.header("Authorization")?.replace("Bearer ", "");
  if (!token) {
    return res.status(401).json({ error: "Access denied. No token provided." });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(400).json({ error: "Invalid token." });
  }
};

const authRoutes = require("./routes/authRoutes");
app.use("/api/auth", authRoutes);
const frontendPath = path.join(__dirname, "../frontend/dist");
app.use(express.static(frontendPath));
app.get("*", (req, res) => {
  if (req.originalUrl.startsWith("/api")) {
    return res.status(404).json({ error: "API route not found" });
  }
  res.sendFile(path.join(frontendPath, "index.html"));
});

app.listen(PORT,"0.0.0.0", () => {
  console.log(`Server is running on port ${PORT}`);
});
