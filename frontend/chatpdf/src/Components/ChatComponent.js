import React, { useState } from "react";

export default function ChatComponent() {
  const [messages, setMessages] = useState([
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
    { isUserSent: false, message: "It's over Anakin, I have the high ground." },
    { isUserSent: true, message: "You underestimate my power!" },
  ]);

  return (
    <div className="p-8 overflow-y-scroll">
      {messages.map((message, index) => (
        <div
          className={`chat ${message.isUserSent ? "chat-end" : "chat-start"}`}
          key={index}
        >
          <div className="chat-bubble">{message.message}</div>
        </div>
      ))}
    </div>
    //   <div className="chat chat-start">
    //     <div className="chat-bubble">
    //       It's over Anakin, <br />I have the high ground.
    //     </div>
    //   </div>
    //   <div className="chat chat-end">
    //     <div className="chat-bubble">You underestimate my power!</div>
    //   </div>
    // </>
  );
}
