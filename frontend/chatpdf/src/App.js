import "./App.css";
import ChatComponent from "./Components/ChatComponent";
import Drawer from "./Components/Drawer";
import TextInput from "./Components/TextInput";

import React, { useEffect, useState } from "react";
import { queryPDF, getChatHistory } from "./Network/Requests";
import ErrorToast from "./Components/ErrorToast";

function ChatPage() {
  const [selectedChat, setSelectedChat] = useState(null);
  const [chats, setChats] = useState([
    // {
    //   chatName: "Anakin",
    //   chatId: 123,
    // },
  ]);

  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getChats = async () => {
      const response = await fetch("http://localhost:8080/chats");
      if (response.status !== 200) {
        showError("Failed to fetch chats");
        return;
      }
      const c = await response.json();
      setChats(c.chats); // Append because we have a default for now
    };
    getChats();
  }, []);

  useEffect(() => {
    // Fetch messages for selected chat
    const getMessages = async () => {
      if (!selectedChat) return;
      setIsLoading(true);
      const response = await getChatHistory(selectedChat.chatId);
      if (response.status !== 200) {
        showError("Failed to fetch chat history");
        setIsLoading(false);
        return;
      }
      const data = await response.json();
      console.log(data);
      setMessages(data.chat_history);
      setIsLoading(false);
    };
    getMessages();
  }, [selectedChat]);

  const onChangeHandler = async (value) => {
    setUserInput(value);
  };

  const onEnterPressedHandler = async () => {
    if (isSending) return;
    setMessages([...messages, { isUserSent: true, message: userInput }]);
    setUserInput("");
    setIsSending(true);
    let response = await queryPDF(selectedChat.chatId, userInput);
    if (response.status !== 200) {
      let data = await response.json()
      showError("Failed to send message: " +  data.error);
      setIsSending(false);
      return;
    }
    let data = await response.json();
    // Append to chat history
    setMessages((prevState) => [
      ...prevState,
      { isUserSent: false, message: data.output },
      // { isUserSent: false, message: "test" },
    ]);

    setIsSending(false);
    // Clear input
  };

  const showError = (message) => {
    setError(message);
    setTimeout(() => {
      setError(null);
    }, 3000);
  };

  return (
    <div className="flex flex-col lg:flex-row h-screen">
      <Drawer
        chats={chats}
        setChats={setChats}
        selectedChat={selectedChat}
        setSelectedChat={setSelectedChat}
      />
      <div className="w-full flex flex-col-reverse">
        <TextInput
          className="sticky bottom-0 z-10 bg-base"
          disabled={selectedChat === null}
          isLoading={isSending}
          value={userInput}
          onChange={(value) => {
            onChangeHandler(value);
          }}
          onEnterPressed={onEnterPressedHandler}
        />
        <ChatComponent
          isLoading={isLoading}
          isSending={isSending}
          messages={messages}
          selectedChat={selectedChat}
        />
      </div>
      {error && <ErrorToast errorDescription={error} />}
    </div>
  );
}

function UploadPage() {
  return <h1>hi</h1>;
}

function App() {
  // return UploadPage();
  return <ChatPage />;
}

export default App;
