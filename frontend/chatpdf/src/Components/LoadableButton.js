import React from "react";
import paperplane from "../Assets/paperplane.svg";

export default function LoadableButton(props) {
  return (
    <>
      {props.isLoading ? (
        <button className="btn btn-square">
          <span className="loading loading-spinner"></span>
        </button>
      ) : (
        <button className={`btn btn-square ${props.disabled ? "btn-disabled" : "btn-primary" }`} onClick={props.onClick}>
          <img src={paperplane} alt="send" />
        </button>
      )}
    </>
  );
}
