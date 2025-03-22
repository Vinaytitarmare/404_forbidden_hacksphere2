import React from 'react'
import Header from './components/Header.jsx'
// import Aurora from "./components/reactbit_components/Aurora"; 
import { Outlet } from 'react-router-dom'

function Layout() {
  return (
    <>
   

      <div className="relative z-10 min-h-screen flex flex-col w-full bg-gray-900">
        <Header />
        <div className="">
          <Outlet />
        </div>
      </div>
    </>
  )
}

export default Layout
