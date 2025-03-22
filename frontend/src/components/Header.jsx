import React from "react";

function Header() {
  return (
    <nav className="flex justify-between items-center p-4 bg-gray-900 text-white shadow-md w-full">
      {/* Logo on the Left */}
      <div className="text-2xl font-bold">BlockVerify</div>

      {/* Profile Image on the Right */}
      <div className="w-10 h-10">
        <img
          src="https://imgs.search.brave.com/qlJCJCDDcSIp5FPo4dbR9jr6jhs9zKJ-AdVifvkvrxQ/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/cGl4YWJheS5jb20v/cGhvdG8vMjAxNC8x/MS8yOS8xOS8zMy9i/YWxkLWVhZ2xlLTU1/MDgwNF82NDAuanBn"
          alt="Profile"
          className="w-full h-full rounded-full border-[1px] border-solid "
        />
      </div>
    </nav>
  );
}

export default Header;
