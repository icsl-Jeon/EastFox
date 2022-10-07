import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { AppState } from "../store/store";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../store/store";
import { fetchStrategy } from "../store/strategy";

export default function Canvas() {
  const loginStatus = useSelector((state: AppState) => state.login);
  const dispatch: AppDispatch = useDispatch();

  useEffect(() => {
    if (loginStatus.status === "succeeded") {
      console.log("Will load strategy here.");
      dispatch(fetchStrategy(loginStatus.userInfo.access_token));
    }
  }, [loginStatus]);

  return loginStatus.status === "succeeded" ? (
    <div>Keep working! </div>
  ) : (
    <div>Please login first.</div>
  );
}
