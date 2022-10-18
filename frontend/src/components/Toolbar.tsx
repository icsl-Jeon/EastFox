import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { AppDispatch, AppState } from "../store/store";
import { ElementType } from "../types/type";
import interactionSlice from "../store/interaction";

export default function Toolbar() {
  const interactionState = useSelector((state: AppState) => state.interaction);
  const dispatch: AppDispatch = useDispatch();

  return (
    <div>
      <input
        type={"radio"}
        checked={interactionState.createTarget === ElementType.Strategist}
        onChange={() =>
          dispatch(
            interactionSlice.actions.setCreateTarget(ElementType.Strategist)
          )
        }
      />
      Strategist
      <input
        type={"radio"}
        checked={interactionState.createTarget === ElementType.Filter}
        onChange={() =>
          dispatch(interactionSlice.actions.setCreateTarget(ElementType.Filter))
        }
      />
      Filter
    </div>
  );
}
