import {
  ElementType,
  InteractionMode,
  Point,
  Rectangle,
  Timeline,
  Screener,
  UserInteraction,
} from "../types/type";
import {
  checkInsideRectangle,
  deriveInteractionModeFromHoverMousePosition,
  findClosestPointFromPointList,
  getCenterPointListFromFourSide,
  getRectangleFromElement,
} from "../types/utility";
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PARAM_ELEMENT } from "../types/constant";

const initialInteraction: UserInteraction = {
  clickedSelectionRectangle: { p1: { x: 0, y: 0 }, p2: { x: 0, y: 0 } },
  isClicked: false,
  mode: InteractionMode.Idle,
  createElementType: ElementType.Timeline,
  currentMousePosition: { x: 0, y: 0 },
  focusedElementList: [],
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState: initialInteraction,
  reducers: {
    setCreateTarget: (state, action: PayloadAction<ElementType>) => {
      state.createElementType = action.payload;
    },
    setInteractionMode: (state, action: PayloadAction<InteractionMode>) => {
      state.mode = action.payload;
    },
    handleMouseDownInteraction: (state, action: PayloadAction<Point>) => {
      let selectionRectangle: undefined | Rectangle;
      const currentMousePosition = state.currentMousePosition;
      switch (state.mode) {
        case InteractionMode.Connect:
          if (state.focusedElementList.length !== 1) break;
          const focusedScreener = state.focusedElementList[0];
          if (focusedScreener.type !== ElementType.Screener) break;
          const rectangle = getRectangleFromElement(focusedScreener);
          const anchorPointList = getCenterPointListFromFourSide(rectangle);
          const closestAnchorPoint = findClosestPointFromPointList(
            currentMousePosition,
            anchorPointList
          );
          selectionRectangle = {
            p1: closestAnchorPoint,
            p2: currentMousePosition,
          };
          break;

        default:
          selectionRectangle = {
            p1: currentMousePosition,
            p2: currentMousePosition,
          };
          break;
      }

      state.isClicked = true;
      if (selectionRectangle)
        state.clickedSelectionRectangle = selectionRectangle;
    },
    handleMouseMoveInteraction: (
      state,
      action: PayloadAction<{
        mousePosition: Point;
        elementList: Array<Timeline | Screener>;
      }>
    ) => {
      state.currentMousePosition = action.payload.mousePosition;

      if (!state.isClicked) {
        for (const element of action.payload.elementList) {
          const interactionMode = deriveInteractionModeFromHoverMousePosition(
            state.currentMousePosition,
            element
          );
          if (!interactionMode) continue;
          if (state.mode !== InteractionMode.Create)
            state.mode = interactionMode;
          if (interactionMode !== InteractionMode.Idle) {
            state.focusedElementList = [element];
            return;
          }
        }
        state.focusedElementList = [];
      }

      if (state.isClicked) {
        const currentClickedMousePosition = state.currentMousePosition;
        state.clickedSelectionRectangle.p2 = currentClickedMousePosition;
        switch (state.mode) {
          case InteractionMode.Create:
            switch (state.createElementType) {
              case ElementType.Timeline:
                state.clickedSelectionRectangle.p2 = {
                  x: action.payload.mousePosition.x,
                  y:
                    state.clickedSelectionRectangle.p1.y +
                    PARAM_ELEMENT.timelineThickness,
                };
                break;

              case ElementType.Screener:
                state.clickedSelectionRectangle.p2 = {
                  x: action.payload.mousePosition.x,
                  y: action.payload.mousePosition.y,
                };
            }
            break;

          case InteractionMode.Idle:
            state.clickedSelectionRectangle.p2 = {
              x: action.payload.mousePosition.x,
              y: action.payload.mousePosition.y,
            };
            break;
          case InteractionMode.Connect:
            const connectOriginScreener = state.focusedElementList[0];
            const connectableTimeline = action.payload.elementList.find(
              (element) => {
                return (
                  element.type === ElementType.Timeline &&
                  checkInsideRectangle(
                    currentClickedMousePosition,
                    getRectangleFromElement(element),
                    PARAM_ELEMENT.elementPointRadius
                  )
                );
              }
            );
            state.focusedElementList = connectableTimeline
              ? [connectOriginScreener, connectableTimeline]
              : [connectOriginScreener];
            break;
        }
      }
    },
    handleMouseUpInteraction: (state) => {
      state.isClicked = false;
      // state.mode = InteractionMode.Idle;
    },
  },
});

export default interactionSlice;
