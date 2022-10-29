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
import {
  addFilterApplication,
  getFilterApplicationList,
} from "../store/filterApplication";

import interactionSlice from "../store/interaction";
import { Status } from "../store/login";
import { PARAMETERS } from "../types/constant";
import {
  ElementType,
  Filter,
  FilterApplication,
  InteractionMode,
  Point,
  Strategist,
} from "../types/type";
import ElementResizeListener from "./ElementResizeListener";
import {
  renderFilterApplicationList,
  renderFilterList,
  renderInteraction,
  renderStrategy,
} from "./Render";

const convertPinDateListToPointList = (strategist: Strategist) => {
  const dateStart = new Date(strategist.dateStart);
  const dateEnd = new Date(strategist.dateEnd);
  const pinPointList = strategist.pinDateList.map((date) => {
    const pinDate = new Date(date);
    const timeDifference = pinDate.valueOf() - dateStart.valueOf();
    const maxTimeDifference = dateEnd.valueOf() - dateStart.valueOf();
    return {
      x:
        strategist.x1 +
        (timeDifference / maxTimeDifference) * (strategist.x2 - strategist.x1),
      y: 0.5 * (strategist.y1 + strategist.y2),
    };
  });
  return pinPointList;
};
const computeDistanceBetweenPoints = (point1: Point, point2: Point) => {
  return Math.sqrt(
    Math.pow(point1.x - point2.x, 2) + Math.pow(point1.y - point2.y, 2)
  );
};

export default function Canvas() {
  const loginState = useSelector((state: AppState) => state.login);
  const strategyState = useSelector((state: AppState) => state.strategy);
  const filterState = useSelector((state: AppState) => state.filter);
  const filterApplicationState = useSelector(
    (state: AppState) => state.filterApplication
  );

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
      dispatch(getStrategy(loginState.userInfo.access_token));
      dispatch(getFilterList(loginState.userInfo.access_token));
      dispatch(getFilterApplicationList(loginState.userInfo.access_token));
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
    renderFilterList(context, filterState.filterList);
    renderFilterApplicationList(
      context,
      filterApplicationState.filterApplicationList
    );
  }, [
    canvasDimension,
    loginState,
    strategyState,
    filterState,
    filterApplicationState,
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
    dispatch(
      interactionSlice.actions.handleMouseMove({
        mousePosition: pointOnCanvas,
        elementList: [
          ...strategyState.strategistList,
          ...filterState.filterList,
        ],
      })
    );
  };

  const handleMouseUp = (event: MouseEvent<HTMLCanvasElement>) => {
    dispatch(interactionSlice.actions.handleMouseUp());
    const modeBeforeMouseUp = interactionState.mode;
    switch (modeBeforeMouseUp) {
      case InteractionMode.Create:
        if (interactionState.createTarget === ElementType.Strategist) {
          const strategist: Strategist = {
            type: ElementType.Strategist,
            dateStart: "1980-01-01",
            dateEnd: "2020-12-31",
            name: `${new Date().toLocaleDateString()}`,
            x1: interactionState.clickedSelectionRectangle.p1.x,
            y1: interactionState.clickedSelectionRectangle.p1.y,
            x2: interactionState.clickedSelectionRectangle.p2.x,
            y2: interactionState.clickedSelectionRectangle.p2.y,
            pinDateList: ["2000-01-01", "2010-01-01"],
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
            type: ElementType.Filter,
            x1: interactionState.clickedSelectionRectangle.p1.x,
            y1: interactionState.clickedSelectionRectangle.p1.y,
            x2: interactionState.clickedSelectionRectangle.p2.x,
            y2: interactionState.clickedSelectionRectangle.p2.y,
          };
          if (
            Math.abs((filter.x2 - filter.x1) * (filter.y2 - filter.y1)) >
            PARAMETERS.minimumAreaForFilter
          )
            dispatch(
              addFilter({
                accessToken: loginState.userInfo.access_token,
                newFilter: filter,
              })
            );
        }
        break;
      case InteractionMode.Connect:
        const focusTargetList = interactionState.focusTargetList;
        if (focusTargetList.length !== 2) break;
        if (focusTargetList[1].type !== ElementType.Strategist) break;
        const pinPointList: Array<Point> = convertPinDateListToPointList(
          focusTargetList[1]
        );
        const dockablePoint = pinPointList.find(
          (point) =>
            computeDistanceBetweenPoints(
              point,
              interactionState.clickedSelectionRectangle.p2
            ) < PARAMETERS.dockingRadius
        );
        if (!dockablePoint) break;
        if (!focusTargetList[0].id || !focusTargetList[1].id) break;
        const dockableIndex = pinPointList.indexOf(dockablePoint);
        const newFilterApplication: FilterApplication = {
          filterId: focusTargetList[0].id,
          strategistId: focusTargetList[1].id,
          appliedDate: focusTargetList[1].pinDateList[dockableIndex],
          x1: interactionState.clickedSelectionRectangle.p1.x,
          y1: interactionState.clickedSelectionRectangle.p1.y,
          x2: dockablePoint.x,
          y2: dockablePoint.y,
        };
        dispatch(
          addFilterApplication({
            accessToken: loginState.userInfo.access_token,
            newFilterApplication: newFilterApplication,
          })
        );

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
