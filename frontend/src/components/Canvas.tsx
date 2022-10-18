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
import { addStrategist, fetchStrategy } from "../store/strategy";
import interactionSlice from "../store/interaction";
import { Status } from "../store/login";
import { PARAMETERS } from "../types/constant";
import {
  ElementType,
  Filter,
  InteractionMode,
  Point,
  Strategist,
} from "../types/type";
import ElementResizeListener from "./ElementResizeListener";
import { renderInteraction, renderStrategy, renderFilterList } from "./Render";
import { addFilter, fetchFilter } from "../store/filter";

export default function Canvas() {
  const loginState = useSelector((state: AppState) => state.login);
  const strategyState = useSelector((state: AppState) => state.strategy);
  const filterState = useSelector((state: AppState) => state.filter);
  const interactionState = useSelector((state: AppState) => state.interaction);
  const dispatch: AppDispatch = useDispatch();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [canvasDimension, setCanvasDimension] = useState<{
    width: number;
    height: number;
  }>({ width: 0, height: 0 });

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
    if (loginState.status === Status.Succeeded) {
      dispatch(fetchStrategy(loginState.userInfo.access_token));
      dispatch(fetchFilter(loginState.userInfo.access_token));
      dispatch(
        interactionSlice.actions.setInteractionMode(InteractionMode.Create)
      );
    }
  }, [loginState]);

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
    renderInteraction(context, interactionState);
    renderStrategy(context, strategyState);
    renderFilterList(context, filterState.filter_list);
  }, [
    canvasDimension,
    loginState,
    strategyState,
    filterState,
    interactionState,
  ]);

  const getCurrentMousePointOnCanvas = (
    event: MouseEvent<HTMLCanvasElement>
  ) => {
    if (!canvasRef.current) return { x: -1, y: -1 };
    const { clientX, clientY } = event;
    const boundingRect = canvasRef.current.getBoundingClientRect();
    const pointOnCanvas: Point = {
      x: clientX - boundingRect.left,
      y: clientY - boundingRect.top,
    };
    return pointOnCanvas;
  };

  const handleMouseDown = (event: MouseEvent<HTMLCanvasElement>) => {
    const pointOnCanvas = getCurrentMousePointOnCanvas(event);
    dispatch(interactionSlice.actions.handleMouseDown(pointOnCanvas));
  };

  const handleMouseMove = (event: MouseEvent<HTMLCanvasElement>) => {
    const pointOnCanvas = getCurrentMousePointOnCanvas(event);
    dispatch(interactionSlice.actions.handleMouseMove(pointOnCanvas));
  };

  const handleMouseUp = (event: MouseEvent<HTMLCanvasElement>) => {
    dispatch(interactionSlice.actions.handleMouseUp());
    if (interactionState.mode === InteractionMode.Create) {
      if (interactionState.createTarget === ElementType.Strategist) {
        const strategist: Strategist = {
          dateStart: new Date(1980, 1, 1),
          dateEnd: new Date(2020, 12, 31),
          name: `${new Date().toLocaleDateString()}`,
          x1: interactionState.selectionRectangle.p1.x,
          y1: interactionState.selectionRectangle.p1.y,
          x2: interactionState.selectionRectangle.p2.x,
          y2: interactionState.selectionRectangle.p2.y,
        };
        dispatch(
          addStrategist({
            accessToken: loginState.userInfo.access_token,
            newStrategist: strategist,
          })
        );
      }
      if (interactionState.createTarget === ElementType.Filter) {
        const filter: Filter = {
          x1: interactionState.selectionRectangle.p1.x,
          y1: interactionState.selectionRectangle.p1.y,
          x2: interactionState.selectionRectangle.p2.x,
          y2: interactionState.selectionRectangle.p2.y,
        };
        dispatch(
          addFilter({
            accessToken: loginState.userInfo.access_token,
            newFilter: filter,
          })
        );
      }
    }
  };

  return loginState.status === Status.Succeeded ? (
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
