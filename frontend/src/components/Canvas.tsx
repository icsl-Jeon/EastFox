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
import { addStrategist, getStrategy } from "../store/strategy";
import { addFilter, getFilterList } from "../store/filter";
import { getSegmentList, computeSegmentForStrategist } from "../store/segment";
import {
  addFilterApplication,
  getFilterApplicationList,
} from "../store/filterApplication";

import interactionSlice from "../store/interaction";
import { Status } from "../store/login";
import { PARAM_ELEMENT, PARAM_LAYOUT } from "../types/constant";
import { ElementType, InteractionMode } from "../types/type";
import {
  deriveStrategistFromInteraction,
  deriveFilterFromInteraction,
  deriveFilterApplicationFromInteraction,
  getCurrentMousePointOnCanvas,
} from "../types/utility";
import ElementResizeListener from "./ElementResizeListener";
import {
  renderFilterApplicationList,
  renderFilterList,
  renderInteraction,
  renderStrategy,
} from "./Render";

export default function Canvas() {
  const loginState = useSelector((state: AppState) => state.login);
  const strategyState = useSelector((state: AppState) => state.strategy);
  const filterState = useSelector((state: AppState) => state.filter);
  const filterApplicationState = useSelector(
    (state: AppState) => state.filterApplication
  );
  const segmentState = useSelector((state: AppState) => state.segment);
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
      height: PARAM_LAYOUT.canvasHeight,
    });
  }, []);

  const initializeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas || !canvas.parentElement || !canvas.getContext("2d")) return;
    const context = canvas.getContext("2d");
    context?.clearRect(0, 0, canvas.width, canvas.height);

    if (canvasDimension.height === 0) {
      canvas.width = canvas.parentElement.getBoundingClientRect().width;
      canvas.height = PARAM_LAYOUT.canvasHeight;
    } else {
      canvas.width = canvasDimension.width;
      canvas.height = canvasDimension.height;
    }
  };

  const dispatchAddElement = () => {
    if (interactionState.createElementType === ElementType.Strategist) {
      const strategist = deriveStrategistFromInteraction(interactionState);
      if (!strategist) return;
      dispatch(
        addStrategist({
          accessToken: loginState.userInfo.access_token,
          newStrategist: strategist,
        })
      );
    }
    if (interactionState.createElementType === ElementType.Filter) {
      const filter = deriveFilterFromInteraction(interactionState);
      if (!filter) return;
      dispatch(
        addFilter({
          accessToken: loginState.userInfo.access_token,
          newFilter: filter,
        })
      );
    }
  };

  const dispatchAddFilterApplicationAndSegment = () => {
    const newFilterApplication =
      deriveFilterApplicationFromInteraction(interactionState);
    if (!newFilterApplication) return;
    dispatch(
      addFilterApplication({
        accessToken: loginState.userInfo.access_token,
        newFilterApplication: newFilterApplication,
      })
    );

    dispatch(
      computeSegmentForStrategist({
        accessToken: loginState.userInfo.access_token,
        strategistId: newFilterApplication.strategistId,
      })
    );
  };

  useEffect(() => {
    if (loginState.status === Status.Succeeded) {
      dispatch(getStrategy(loginState.userInfo.access_token));
      dispatch(getFilterList(loginState.userInfo.access_token));
      dispatch(getFilterApplicationList(loginState.userInfo.access_token));
      dispatch(getSegmentList(loginState.userInfo.access_token));

      dispatch(
        interactionSlice.actions.setInteractionMode(InteractionMode.Create)
      );
    }
  }, [loginState]);

  useLayoutEffect(() => {
    initializeCanvas();
    const context = canvasRef.current?.getContext("2d");
    if (!context) return;
    renderStrategy(context, strategyState);
    renderFilterList(context, filterState.filterList);
    renderFilterApplicationList(
      context,
      filterApplicationState.filterApplicationList
    );
    renderInteraction(context, interactionState);
  }, [
    canvasDimension,
    loginState,
    strategyState,
    filterState,
    filterApplicationState,
    segmentState,
    interactionState,
  ]);

  const handleMouseDown = (event: MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const pointOnCanvas = getCurrentMousePointOnCanvas(
      event,
      canvasRef.current
    );
    dispatch(
      interactionSlice.actions.handleMouseDownInteraction(pointOnCanvas)
    );
  };

  const handleMouseMove = (event: MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const pointOnCanvas = getCurrentMousePointOnCanvas(
      event,
      canvasRef.current
    );
    dispatch(
      interactionSlice.actions.handleMouseMoveInteraction({
        mousePosition: pointOnCanvas,
        elementList: [
          ...strategyState.strategistList,
          ...filterState.filterList,
        ],
      })
    );
  };

  const handleMouseUp = (event: MouseEvent<HTMLCanvasElement>) => {
    dispatch(interactionSlice.actions.handleMouseUpInteraction());
    const modeBeforeMouseUp = interactionState.mode;
    switch (modeBeforeMouseUp) {
      case InteractionMode.Create:
        dispatchAddElement();
        break;
      case InteractionMode.Connect:
        dispatchAddFilterApplicationAndSegment();
        break;
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
