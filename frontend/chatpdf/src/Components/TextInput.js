import React from "react";
import LoadableButton from "./LoadableButton";

export default function TextInput({
  disabled,
  className,
  onChange,
  onEnterPressed,
  value,
  isLoading,
  placeholder
}) {
  return (
    <div className={`pt-4 w-full flex gap-4 ${className}`}>
      <input
        disabled={disabled}
        type="text"
        placeholder={placeholder || "Type here"}
        value={value}
        className="input input-bordered input-primary w-full"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onEnterPressed();
          }
        }}
      />
      <LoadableButton disabled={disabled || value === ""} isLoading={isLoading} onClick={onEnterPressed}/>
    </div>
  );
}
