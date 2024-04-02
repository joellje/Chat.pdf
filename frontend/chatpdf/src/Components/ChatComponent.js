import React, { useEffect, useRef, useState } from "react";
import { getChatHistory } from "../Network/Requests";
import ErrorToast from "./ErrorToast";

export default function ChatComponent({
  isLoading,
  isSending,
  messages,
  selectedChat,
}) {
  const messageRef = useRef(null);

  // Update scroll position whenever messages change
  useEffect(() => {
    // Scroll to bottom whenever loading changes
    console.log("scrolling");
    console.log(messageRef.current);
    if (messageRef.current) {
      messageRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  if (isLoading) {
    return (
      <div className="text-center">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  return (
    <div className="p-8 pb-2 overflow-y-scroll">
      {selectedChat ? (
        messages && messages.length > 0 ? (
          <>
            {messages.map((message, index) => (
              <div
                className={`chat ${
                  message.isUserSent ? "chat-end" : "chat-start"
                }`}
                key={index}
              >
                <div
                  className={`chat-bubble ${
                    message.isUserSent ? "chat-bubble-primary" : ""
                  }`}
                >
                  {message.message}
                </div>
                <div ref={messageRef}></div>
              </div>
            ))}
            {isSending && (
              <div className={`chat chat-start`}>
                <div className={`chat-bubble`}>
                  <span className="loading loading-spinner"></span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-2xl">Ask me anything!</div>
        )
      ) : (
        <div className="text-center text-2xl">
          Upload a file or select a chat to start
        </div>
      )}
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
