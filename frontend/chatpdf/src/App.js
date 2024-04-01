import "./App.css";
import ChatComponent from "./Components/ChatComponent";
import Drawer from "./Components/Drawer";
import TextInput from "./Components/TextInput";
// import ChatComponent from "./ChatComponent";

function App() {
  return (
    // <div className="flex">
    // <TextInput />

    <div className="lg:flex h-screen">
      <Drawer />
      {/* <div className="overflow-y-scroll"> */}
      <div className="w-full flex flex-col-reverse">
        <TextInput className="" />
        <ChatComponent />
      </div>
      {/* </div> */}
    </div>
    // </div>
  );
}

export default App;
