const API_URL = "http://localhost:8080";

const createUUID = () => {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = (Math.random() * 16) | 0,
            v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
};

export const uploadPDF = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("chat_id", createUUID());

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    return response;
};

export const queryPDF = async (chatId, query) => {
    // Post with body
    console.log(chatId, query);
    const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ chat_id: chatId, query: query }),
    });
    return response;
};

export const getChats = async () => {
    const response = await fetch(`${API_URL}/chats`);
    return response;
};

export const getChatHistory = async (chatId) => {
    const response = await fetch(`${API_URL}/chatHistory?chat_id=${chatId}`);
    return response;
};
