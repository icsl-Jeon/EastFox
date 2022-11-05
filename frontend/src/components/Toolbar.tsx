import React, { useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { AppDispatch, AppState } from "../store/store";
import { ElementType } from "../types/type";
import interactionSlice from "../store/interaction";
import Button from "react-bootstrap/Button";

export default function Toolbar() {
  const interactionState = useSelector((state: AppState) => state.interaction);
  const dispatch: AppDispatch = useDispatch();
  const handleButtonClick = (event: React.MouseEvent) => {
    event.preventDefault();
    const { value } = event.target as HTMLButtonElement;
    const elementType: ElementType =
      ElementType[value as keyof typeof ElementType];
    console.log(elementType);
    dispatch(interactionSlice.actions.setCreateTarget(elementType));
  };

  const buttonType = [ElementType.Strategist, ElementType.Filter];
  return (
    <div>
      {buttonType.map((item, index) => (
        <Button
          key={index}
          name={item}
          value={item}
          onClick={handleButtonClick}
          variant={
            interactionState.createElementType === item
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
