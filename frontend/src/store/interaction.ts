import {
  ElementType,
  InteractionMode,
  Point,
  UserInteraction,
} from "../types/type";
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PARAMETERS } from "../types/constant";

const initialInteraction: UserInteraction = {
  selectionRectangle: { p1: { x: 0, y: 0 }, p2: { x: 0, y: 0 } },
  whileClick: false,
  mode: InteractionMode.Select,
  createTarget: ElementType.Strategist,
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
      state.selectionRectangle = { p1: action.payload, p2: action.payload };
    },
    handleMouseMove: (state, action: PayloadAction<Point>) => {
      if (!state.whileClick) return;
      if (state.mode === InteractionMode.Create) {
        if (state.createTarget === ElementType.Strategist) {
          state.selectionRectangle.p2 = {
            x: action.payload.x,
            y:
              state.selectionRectangle.p1.y + PARAMETERS.strategyRectangleWidth,
          };
        }
        if (state.createTarget === ElementType.Filter) {
          state.selectionRectangle.p2 = {
            x: action.payload.x,
            y: action.payload.y,
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
