import Canvas from "../components/Canvas";
import Login from "../components/Login";
import { useSelector } from "react-redux";
import { AppState } from "../store/store";
import { Status } from "../store/login";
import CreateTargetSelector from "../components/CreateTargetSelector";

export default function CanvasPage() {
  const loginStatus = useSelector((state: AppState) => state.login);

  return (
    <div>
      <h2>Welcome to canvas page!</h2>
      {loginStatus.status === Status.Failed ||
      loginStatus.status === Status.Idle ? (
        <Login />
      ) : (
        <div>
          <CreateTargetSelector />
          <Canvas />
        </div>
      )}
    </div>
  );
}
