import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { AppState } from "../store/store";

export default function Canvas() {
  const loginState = useSelector((state: AppState) => state.login);
  return loginState.status === "succeeded" ? (
    <div>Keep working! </div>
  ) : (
    <div>Please login first.</div>
  );
}
