import React, {
  MouseEvent,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, AppState } from "../store/store";
import { fetchStrategy } from "../store/strategy";
import CanvasElement, {
  InteractionMode,
  PARAMETERS,
  UserInteraction,
} from "./CanvasElement";
import { Status } from "../store/user";
import ElementResizeListener from "./ElementResizeListener";

export default function Canvas() {
  const loginStatus = useSelector((state: AppState) => state.login);
  const dispatch: AppDispatch = useDispatch();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [canvasElementList, setCanvasElementList] = useState<
    Array<CanvasElement>
  >([]);
  const [canvasDimension, setCanvasDimension] = useState<{
    width: number;
    height: number;
  }>({ width: 0, height: 0 });
  const userInteractionRef = useRef<UserInteraction>(new UserInteraction());
  const elementCreateIndexRef = useRef<number>(0);

  const adaptResize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (!canvas.parentElement) return;
    const elmRect = canvas.parentElement.getBoundingClientRect();
    setCanvasDimension({
      width: elmRect.width,
      height: PARAMETERS.canvasHeight,
    });
  }, []);

  useEffect(() => {
    if (loginStatus.status === Status.Succeeded) {
      dispatch(fetchStrategy(loginStatus.userInfo.access_token));
    }
  }, [loginStatus]);

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !canvas.parentElement || !canvas.getContext("2d")) return;
    const context = canvas.getContext("2d");

    context?.clearRect(0, 0, canvas.width, canvas.height);

    if (canvasDimension.height === 0) {
      canvas.width = canvas.parentElement.getBoundingClientRect().width;
      canvas.height = PARAMETERS.canvasHeight;
    } else {
      canvas.width = canvasDimension.width;
      canvas.height = canvasDimension.height;
    }
  }, [canvasElementList, canvasDimension, loginStatus]);

  const handleMouseDown = (event: MouseEvent<HTMLCanvasElement>) => {
    const { clientX, clientY } = event;
    userInteractionRef.current.whileClick = true;
    userInteractionRef.current.lastClickedPoint.x = clientX;
    userInteractionRef.current.lastClickedPoint.y = clientY;
    if (userInteractionRef.current.mode === InteractionMode.Create) {
    }
  };

  const handleMouseMove = (event: MouseEvent<HTMLCanvasElement>) => {
    const { clientX, clientY } = event;
    if (!userInteractionRef.current.whileClick) return;
    if (userInteractionRef.current.mode === InteractionMode.Create) {
    }
  };

  const handleMouseUp = (event: MouseEvent<HTMLCanvasElement>) => {
    const { clientX, clientY } = event;
    userInteractionRef.current.whileClick = false;
  };

  return loginStatus.status === Status.Succeeded ? (
    <div>
      <ElementResizeListener onResize={adaptResize} />
      <canvas
        ref={canvasRef}
        style={{ borderStyle: "solid" }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      ></canvas>
    </div>
  ) : (
    <div>Please login first.</div>
  );
}
