import {
  ElementType,
  Filter,
  InteractionMode,
  Point,
  Rectangle,
  RectangleFocusRegion,
  Strategist,
  UserInteraction,
} from "../types/type";
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PARAMETERS } from "../types/constant";

const initialInteraction: UserInteraction = {
  clickedSelectionRectangle: { p1: { x: 0, y: 0 }, p2: { x: 0, y: 0 } },
  whileClick: false,
  mode: InteractionMode.Idle,
  createTarget: ElementType.Strategist,
  currentMousePosition: { x: 0, y: 0 },
  focusTargetList: [],
};

const checkInsideRectangle = (point: Point, rectangle: Rectangle) => {
  if (
    point.x > rectangle.p1.x &&
    point.x < rectangle.p2.x &&
    point.y > rectangle.p1.y &&
    point.y < rectangle.p2.y
  )
    return true;
  return false;
};

const computeDistanceBetweenPoints = (point1: Point, point2: Point) => {
  return Math.sqrt(
    Math.pow(point1.x - point2.x, 2) + Math.pow(point1.y - point2.y, 2)
  );
};

const computeFocusRegion = (mousePosition: Point, rectangle: Rectangle) => {
  if (
    mousePosition.x < rectangle.p1.x - PARAMETERS.focusEdgeThickness ||
    mousePosition.x > rectangle.p2.x + PARAMETERS.focusEdgeThickness ||
    mousePosition.y < rectangle.p1.y - PARAMETERS.focusEdgeThickness ||
    mousePosition.y > rectangle.p2.y + PARAMETERS.focusEdgeThickness
  )
    return RectangleFocusRegion.Outer;

  const rectangleCenter: Point = {
    x: (rectangle.p1.x + rectangle.p2.x) / 2,
    y: (rectangle.p1.y + rectangle.p2.y) / 2,
  };
  const width = rectangle.p2.x - rectangle.p1.x;
  const height = rectangle.p2.y - rectangle.p1.y;

  const mousePositionWithRespectToCenter: Point = {
    x: Math.abs(mousePosition.x - rectangleCenter.x),
    y: Math.abs(mousePosition.y - rectangleCenter.y),
  };

  const cornerBoundaryRectangleWithRespectToCenter: Rectangle = {
    p1: {
      x: width / 2 - PARAMETERS.focusCornerThickness,
      y: height / 2 - PARAMETERS.focusCornerThickness,
    },
    p2: {
      x: width / 2 + PARAMETERS.focusCornerThickness,
      y: height / 2 + PARAMETERS.focusCornerThickness,
    },
  };

  if (
    checkInsideRectangle(
      mousePositionWithRespectToCenter,
      cornerBoundaryRectangleWithRespectToCenter
    )
  )
    return RectangleFocusRegion.Corner;

  const innerRectangleWithRespectToCenter: Rectangle = {
    p1: {
      x: 0,
      y: 0,
    },
    p2: {
      x: width / 2 - PARAMETERS.focusEdgeThickness,
      y: height / 2 - PARAMETERS.focusEdgeThickness,
    },
  };

  if (
    checkInsideRectangle(
      mousePositionWithRespectToCenter,
      innerRectangleWithRespectToCenter
    )
  )
    return RectangleFocusRegion.Inner;
  if (
    computeDistanceBetweenPoints(
      {
        x: 0,
        y: height / 2,
      },
      mousePositionWithRespectToCenter
    ) < PARAMETERS.dockingRadius ||
    computeDistanceBetweenPoints(
      {
        x: width / 2,
        y: 0,
      },
      mousePositionWithRespectToCenter
    ) < PARAMETERS.dockingRadius
  )
    return RectangleFocusRegion.EdgeCenter;

  return RectangleFocusRegion.Edge;
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState: initialInteraction,
  reducers: {
    setCreateTarget: (state, action: PayloadAction<ElementType>) => {
      state.createTarget = action.payload;
    },
    setInteractionMode: (state, action: PayloadAction<InteractionMode>) => {
      state.mode = action.payload;
    },
    handleMouseDown: (state, action: PayloadAction<Point>) => {
      state.whileClick = true;
      state.currentMousePosition = action.payload;

      if (state.mode !== InteractionMode.Connect) {
        state.clickedSelectionRectangle = {
          p1: state.currentMousePosition,
          p2: state.currentMousePosition,
        };
      } else {
        if (!state.focusTargetList.length) return;
        if (state.focusTargetList[0].type === ElementType.Strategist) return;
        const focusTarget = state.focusTargetList[0];
        let anchorPointList: Array<Point> = [];
        if (focusTarget)
          anchorPointList = [
            { x: focusTarget.x1, y: 0.5 * (focusTarget.y1 + focusTarget.y2) },
            { x: focusTarget.x2, y: 0.5 * (focusTarget.y1 + focusTarget.y2) },
            { x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y1 },
            { x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y2 },
          ];

        const distanceToAnchorPointList = anchorPointList.map(
          (point) =>
            Math.pow(state.currentMousePosition.x - point.x, 2) +
            Math.pow(state.currentMousePosition.y - point.y, 2)
        );
        const minDistance = Math.min(...distanceToAnchorPointList);
        const closestAnchorPoint =
          anchorPointList[distanceToAnchorPointList.indexOf(minDistance)];

        state.clickedSelectionRectangle = {
          p1: closestAnchorPoint,
          p2: state.currentMousePosition,
        };
        // state.focusTargetList = [];
      }
    },
    handleMouseMove: (
      state,
      action: PayloadAction<{
        mousePosition: Point;
        elementList: Array<Strategist | Filter>;
      }>
    ) => {
      state.currentMousePosition = action.payload.mousePosition;
      if (!state.whileClick) {
        state.focusTargetList = [];

        state.mode = InteractionMode.Create;
        for (const element of action.payload.elementList) {
          const boundingRectangle = {
            p1: {
              x: Math.min(element.x1, element.x2),
              y: Math.min(element.y1, element.y2),
            },
            p2: {
              x: Math.max(element.x1, element.x2),
              y: Math.max(element.y1, element.y2),
            },
          };
          const focusRegion = computeFocusRegion(
            action.payload.mousePosition,
            boundingRectangle
          );
          switch (focusRegion) {
            case RectangleFocusRegion.Outer:
              continue;

            case RectangleFocusRegion.Corner:
              state.mode = InteractionMode.Reshape;
              break;

            case RectangleFocusRegion.Inner:
              state.mode = InteractionMode.Translate;
              break;

            case RectangleFocusRegion.EdgeCenter:
              if (element.type === ElementType.Strategist) break;
              else state.mode = InteractionMode.Connect;
              break;
            case RectangleFocusRegion.Edge:
              state.mode = InteractionMode.Translate;
              break;
          }
          state.focusTargetList = [element];
        }
      }

      if (state.whileClick)
        if (state.mode === InteractionMode.Create)
          switch (state.createTarget) {
            case ElementType.Strategist:
              state.clickedSelectionRectangle.p2 = {
                x: action.payload.mousePosition.x,
                y:
                  state.clickedSelectionRectangle.p1.y +
                  PARAMETERS.strategyRectangleWidth,
              };
              break;

            case ElementType.Filter:
              state.clickedSelectionRectangle.p2 = {
                x: action.payload.mousePosition.x,
                y: action.payload.mousePosition.y,
              };
          }
        else if (state.mode === InteractionMode.Connect) {
          state.clickedSelectionRectangle.p2 = {
            x: action.payload.mousePosition.x,
            y: action.payload.mousePosition.y,
          };
          const connectibleElement = action.payload.elementList.find(
            (element) => {
              const connectibleRectangle: Rectangle = {
                p1: {
                  x: element.x1 - PARAMETERS.strategyConnectMargin,
                  y: element.y1 - PARAMETERS.strategyConnectMargin,
                },
                p2: {
                  x: element.x2 + PARAMETERS.strategyConnectMargin,
                  y: element.y2 + PARAMETERS.strategyConnectMargin,
                },
              };
              return (
                element.type === ElementType.Strategist &&
                checkInsideRectangle(
                  action.payload.mousePosition,
                  connectibleRectangle
                )
              );
            }
          );
          if (!connectibleElement) {
            if (state.focusTargetList.length === 2) state.focusTargetList.pop();
            return;
          }
          if (state.focusTargetList.length === 1)
            state.focusTargetList.push(connectibleElement);
          else state.focusTargetList[1] = connectibleElement;
        }
    },
    handleMouseUp: (state) => {
      state.whileClick = false;
      state.mode = InteractionMode.Idle;
    },
  },
});

export default interactionSlice;
