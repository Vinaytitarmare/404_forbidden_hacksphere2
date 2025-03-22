import React from "react";

function Header() {
  return (
    <nav className="flex justify-between items-center p-4 bg-gray-900 text-white shadow-md w-full">
      {/* Logo on the Left */}
      <div className="text-2xl font-bold">BlockVerify</div>

      {/* Profile Image on the Right */}
      <div className="w-10 h-10">
        <img
          src="https://via.placeholder.com/40"
          alt="Profile"
          className="w-full h-full rounded-full"
        />
      </div>
    </nav>
  );
}

export default Header;
