import {
  ElementType,
  Filter,
  InteractionMode,
  Point,
  Rectangle,
  Strategist,
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
import interaction from "./interaction";
import { AppDispatch } from "./store";
import { useDispatch } from "react-redux";

const initialInteraction: UserInteraction = {
  clickedSelectionRectangle: { p1: { x: 0, y: 0 }, p2: { x: 0, y: 0 } },
  isClicked: false,
  mode: InteractionMode.Idle,
  createElementType: ElementType.Strategist,
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
          const focusedFilter = state.focusedElementList[0];
          if (focusedFilter.type !== ElementType.Filter) break;
          const rectangle = getRectangleFromElement(focusedFilter);
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
        elementList: Array<Strategist | Filter>;
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
          case InteractionMode.Idle:
            console.log(
              "Should check included elements inside selection rectangle."
            );
            break;
          case InteractionMode.Connect:
            const connectOriginFilter = state.focusedElementList[0];
            const connectableStrategist = action.payload.elementList.find(
              (element) => {
                return (
                  element.type === ElementType.Strategist &&
                  checkInsideRectangle(
                    currentClickedMousePosition,
                    getRectangleFromElement(element),
                    PARAM_ELEMENT.elementPointRadius
                  )
                );
              }
            );
            state.focusedElementList = connectableStrategist
              ? [connectOriginFilter, connectableStrategist]
              : [connectOriginFilter];
            break;
        }
      }
    },
    handleMouseUpInteraction: (state) => {
      state.isClicked = false;
      state.mode = InteractionMode.Idle;
    },
  },
});

export default interactionSlice;
