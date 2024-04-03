import React, { useState } from "react";
import { FileDrop } from "react-file-drop";
import { uploadPDF, queryPDF } from "../Network/Requests";

export default function Drawer({
  chats,
  setChats,
  selectedChat,
  setSelectedChat,
  // makeQuery,
}) {
  // const [chats, setChats] = useState([
  //   {
  //     chatName: "Anakin",
  //     chatId: 123,
  //   },
  // ]);

  const [isHovering, setIsHovering] = useState(false);
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleDrop = async (files) => {
    setIsUploading(true);
    const response = await uploadPDF(files[0]);
    if (response.status != 200) {
      console.error("Upload failed");
      setIsUploading(false);
      return;
    }
    setIsUploading(false);
    const data = await response.json();
    setChats([...chats, { chatName: data.chatName, chatId: data.chatId }]);
    setSelectedChat({ chatName: data.chatName, chatId: data.chatId });
    // makeQuery(
    //   data.chatId,
      
    // );
  };

  const uploadFileButton = (isDrawer) => (
    <FileDrop
      className={`btn btn-outline btn-primary bg-base btn-lg ${
        isHovering && "bg-success/40"
      } ${
        isDraggingFile
          ? "border-solid shadow-md shadow-primary"
          : "border-dashed"
      } ${isDrawer ? "hidden lg:flex" : "flex lg:hidden"}`}
      onFrameDragEnter={(event) =>
        // console.log("onFrameDragEnter", event)
        // setIsHovering(true)
        setIsDraggingFile(true)
      }
      onFrameDragLeave={(event) =>
        // console.log("onFrameDragLeave", event)
        // setIsHovering(false)
        setIsDraggingFile(false)
      }
      onFrameDrop={(event) => {
        isDraggingFile && setIsDraggingFile(false);
        isHovering && setIsHovering(false);
      }}
      onDragOver={(event) =>
        // console.log("onDragOver", event)
        setIsHovering(true)
      }
      onDragLeave={(event) =>
        // console.log("onDragLeave", event)
        setIsHovering(false)
      }
      onDrop={(files, event) => handleDrop(files)}
      onTargetClick={(e) => {
        document.getElementById("file").click();
      }}
    >
      {isUploading ? (
        <span className="loading"></span>
      ) : (
        <>
          New Chat
          <div className="text-xs">Drop PDF here</div>
        </>
      )}
    </FileDrop>
  );

  return (
    <div className="z-20">
      <div className="drawer lg:drawer-open bg-base-300">
        <input id="my-drawer-2" type="checkbox" className="drawer-toggle" />
        <div className="drawer-content flex items-center justify-center gap-8 p-8 lg:p-0">
          {uploadFileButton(false)}
          <label
            htmlFor="my-drawer-2"
            className="btn drawer-button btn-lg text-sm lg:hidden"
          >
            View Chat History
          </label>
        </div>
        <div className="drawer-side z-30">
          <label
            htmlFor="my-drawer-2"
            aria-label="close sidebar"
            className="drawer-overlay"
          ></label>
          <ul className="menu p-4 w-80 min-h-full text-base-content bg-base-200">
            <li>
              <input
                type="file"
                id="file"
                className="hidden"
                onInputCapture={(e) => {
                  handleDrop(e.currentTarget.files);
                }}
              />
              {uploadFileButton(true)}
            </li>
            <li className="divider"></li>
            <li className="menu-title text-base-content text-xl">Chats</li>
            {chats &&
              chats.map((chat, index) => (
                <li key={index}>
                  <a
                    key={chat.chatId}
                    className={`${
                      selectedChat &&
                      selectedChat.chatId == chat.chatId &&
                      "active"
                    }`}
                    onClick={() => {
                      setSelectedChat(chats[index]);
                    }}
                  >
                    {chat.chatName}
                  </a>
                </li>
              ))}
            {!chats && <li>No chats</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
