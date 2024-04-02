import React, { useState } from "react";

export default function Drawer() {
  const [chats, setChats] = useState([
    {
      chatName: "Anakin",
      chatId: 123,
    },
  ]);
  return (
    <div className="z-20">
      <div className="drawer lg:drawer-open">
        <input id="my-drawer-2" type="checkbox" className="drawer-toggle" />
        <div className="drawer-content flex flex-col items-center justify-center p-8 lg:p-0">
          {/* Page content here */}
          <label
            htmlFor="my-drawer-2"
            className="btn drawer-button lg:hidden"
          >
            View Chat History
          </label>
        </div>
        <div className="drawer-side">
          <label
            htmlFor="my-drawer-2"
            aria-label="close sidebar"
            className="drawer-overlay"
          ></label>
          <ul className="menu p-4 w-80 min-h-full bg-base-200 text-base-content">
            {/* Sidebar content here */}
            <li>
              <button className="btn btn-primary">New Chat</button>
            </li>
            <li className="divider"></li>
            <li className="menu-title text-black text-xl">Chats</li>
            {chats.map((chat, index) => (
              <li key={index}>
                <a>{chat.chatName}</a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
