import React from "react";

export default function ErrorToast({ errorDescription }) {
  return (
    <div className="toast toast-top toast-cente z-20">
      <div className="alert alert-error">
        <span>{errorDescription}</span>
      </div>
    </div>
  );
}
