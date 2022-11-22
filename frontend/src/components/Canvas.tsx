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

import { createTimeline, readTimelineList } from "../store/timeline";
import { createScreener, readScreenerList } from "../store/screener";
import {
  readSegmentList,
  updateSegmentListForTimeline,
} from "../store/segment";
import {
  createScreenerApplication,
  readScreenerApplicationList,
} from "../store/screenerApplication";

import interactionSlice from "../store/interaction";
import { Status } from "../store/login";
import { PARAM_LAYOUT } from "../types/constant";
import { ElementType, InteractionMode } from "../types/type";

import {
  deriveTimelineFromInteraction,
  deriveScreenerFromInteraction,
  deriveScreenerApplicationFromInteraction,
  getCurrentMousePointOnCanvas,
} from "../types/utility";
import ElementResizeListener from "./ElementResizeListener";
import {
  renderScreenerApplicationList,
  renderScreenerList,
  renderInteraction,
  renderTimelineList,
} from "./Render";

export default function Canvas() {
  const loginState = useSelector((state: AppState) => state.login);
  const timelineState = useSelector((state: AppState) => state.timeline);
  const screenerState = useSelector((state: AppState) => state.screener);
  const screenerApplicationState = useSelector(
    (state: AppState) => state.screenerApplication
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

  const dispatchCreateElementFromCreateTargetSelector = () => {
    if (interactionState.createElementType === ElementType.Timeline) {
      const timeline = deriveTimelineFromInteraction(interactionState);
      if (!timeline) return;
      dispatch(
        createTimeline({
          accessToken: loginState.userInfo.access_token,
          newTimeline: timeline,
        })
      );
    }
    if (interactionState.createElementType === ElementType.Screener) {
      const screener = deriveScreenerFromInteraction(interactionState);
      if (!screener) return;
      dispatch(
        createScreener({
          accessToken: loginState.userInfo.access_token,
          newScreener: screener,
        })
      );
    }
  };

  const dispatchCreateScreenerApplicationAndUpdateSegment = () => {
    const newScreenerApplication =
      deriveScreenerApplicationFromInteraction(interactionState);
    if (!newScreenerApplication) return;
    dispatch(
      createScreenerApplication({
        accessToken: loginState.userInfo.access_token,
        newScreenerApplication: newScreenerApplication,
      })
    );

    dispatch(readScreenerApplicationList(loginState.userInfo.access_token));

    dispatch(
      updateSegmentListForTimeline({
        accessToken: loginState.userInfo.access_token,
        timelineId: newScreenerApplication.timelineId,
      })
    );
  };

  useEffect(() => {
    if (loginState.status === Status.Succeeded) {
      dispatch(readTimelineList(loginState.userInfo.access_token));
      dispatch(readScreenerList(loginState.userInfo.access_token));
      dispatch(readScreenerApplicationList(loginState.userInfo.access_token));
      dispatch(readSegmentList(loginState.userInfo.access_token));

      dispatch(
        interactionSlice.actions.setInteractionMode(InteractionMode.Idle)
      );
    }
  }, [loginState]);

  useLayoutEffect(() => {
    initializeCanvas();
    const context = canvasRef.current?.getContext("2d");
    if (!context) return;
    renderTimelineList(context, timelineState);
    renderScreenerList(context, screenerState.screenerList);
    renderScreenerApplicationList(
      context,
      screenerApplicationState.screenerApplicationList
    );
    renderInteraction(context, interactionState);
  }, [
    canvasDimension,
    loginState,
    timelineState,
    screenerState,
    screenerApplicationState,
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
          ...timelineState.timelineList,
          ...screenerState.screenerList,
        ],
      })
    );
  };

  const handleMouseUp = (event: MouseEvent<HTMLCanvasElement>) => {
    dispatch(interactionSlice.actions.handleMouseUpInteraction());
    const modeBeforeMouseUp = interactionState.mode;
    switch (modeBeforeMouseUp) {
      case InteractionMode.Create:
        dispatchCreateElementFromCreateTargetSelector();
        break;
      case InteractionMode.Connect:
        dispatchCreateScreenerApplicationAndUpdateSegment();
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
