import React from "react";
import LoadableButton from "./LoadableButton";

export default function TextInput(props) {
  return (
    <div className={`p-8 w-full flex gap-4 ${props.className}`}>
      <input
        type="text"
        placeholder="Type here"
        className="input input-bordered input-primary w-full"
      />
      <LoadableButton isLoading={false} />
    </div>
  );
}
