import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { AppState } from "../store/store";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../store/store";
import Button from "react-bootstrap/Button";
import loginSlice, { fetchUserByLogin } from "../store/user";

const loginInput = { username: "jbs", password: "jbs4235v" };

export default function Login() {
  const loginStatus = useSelector((state: AppState) => state.login);
  const dispatch: AppDispatch = useDispatch();
  const handleClick = (event: React.MouseEvent) => {
    event.preventDefault();
    const response = dispatch(fetchUserByLogin(loginInput));
    console.log(response);
  };

  return <Button onClick={handleClick}>Login</Button>;
}
