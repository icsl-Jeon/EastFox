import React, { useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { AppDispatch, AppState } from "../store/store";
import { ElementType, InteractionMode } from "../types/type";
import interactionSlice from "../store/interaction";
import Button from "react-bootstrap/Button";

export default function CreateTargetSelector() {
  const interactionState = useSelector((state: AppState) => state.interaction);
  const dispatch: AppDispatch = useDispatch();
  const handleButtonClick = (event: React.MouseEvent) => {
    event.preventDefault();
    const { value } = event.target as HTMLButtonElement;
    const elementType: ElementType =
      ElementType[value as keyof typeof ElementType];
    console.log(elementType);
    if (interactionState.mode === InteractionMode.Create) {
      if (interactionState.createElementType === elementType) {
        dispatch(
          interactionSlice.actions.setInteractionMode(InteractionMode.Idle)
        );
      } else {
        dispatch(interactionSlice.actions.setCreateTarget(elementType));
      }
    } else {
      dispatch(
        interactionSlice.actions.setInteractionMode(InteractionMode.Create)
      );
      dispatch(interactionSlice.actions.setCreateTarget(elementType));
    }
  };

  const buttonType = [ElementType.Timeline, ElementType.Screener];
  return (
    <div>
      {buttonType.map((item, index) => (
        <Button
          key={index}
          name={item}
          value={item}
          onClick={handleButtonClick}
          variant={
            interactionState.createElementType === item &&
            interactionState.mode === InteractionMode.Create
              ? "primary"
              : "secondary"
          }
        >
          {item}
        </Button>
      ))}
    </div>
  );
}
