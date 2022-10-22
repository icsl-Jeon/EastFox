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

  const pointWithRespectToCenter: Point = {
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
      pointWithRespectToCenter,
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
      pointWithRespectToCenter,
      innerRectangleWithRespectToCenter
    )
  )
    return RectangleFocusRegion.Inner;

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
      state.clickedSelectionRectangle = {
        p1: action.payload,
        p2: action.payload,
      };
      state.currentMousePosition = action.payload;
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

            case RectangleFocusRegion.Edge:
              if ("name" in element) state.mode = InteractionMode.Translate;
              else state.mode = InteractionMode.Connect;
              break;
          }
          state.focusTarget = element;
        }
      }

      if (state.whileClick)
        if (state.mode === InteractionMode.Create) {
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
        }
    },
    handleMouseUp: (state) => {
      state.whileClick = false;
    },
  },
});

export default interactionSlice;
