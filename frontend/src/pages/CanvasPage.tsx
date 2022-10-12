import Canvas from "../components/Canvas";
import Login from "../components/Login";
import { useSelector } from "react-redux";
import { AppState } from "../store/store";
import { Status } from "../store/user";

export default function CanvasPage() {
  const loginStatus = useSelector((state: AppState) => state.login);

  return (
    <div>
      <h2>Welcome to canvas page!</h2>
      {(loginStatus.status === Status.Failed ||
        loginStatus.status === Status.Idle) && <Login />}
      <Canvas />
    </div>
  );
}
