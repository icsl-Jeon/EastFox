import {
  ElementType,
  Filter,
  FilterApplication,
  InteractionMode,
  Point,
  Strategy,
  UserInteraction,
} from "../types/type";
import {
  computeDistanceBetweenPoints,
  convertPinDateListToPointList,
  findClosestPointFromPointList,
  getCenterPointListFromFourSide,
  getRectangleFromElement,
} from "../types/utility";
import { PARAM_COLOR, PARAM_RENDER, PARAM_ELEMENT } from "../types/constant";

export const renderInteraction = (
  context: CanvasRenderingContext2D | null,
  interaction: UserInteraction
) => {
  if (!context) return;
  if (interaction.mode === InteractionMode.Idle) return;

  interaction.focusedElementList.forEach((element) => {
    context.strokeStyle = PARAM_COLOR.focus;
    context.lineWidth = PARAM_RENDER.focusThickness;
    const elementRectangle = getRectangleFromElement(element);
    context.strokeRect(
      elementRectangle.p1.x,
      elementRectangle.p1.y,
      elementRectangle.p2.x - elementRectangle.p1.x,
      elementRectangle.p2.y - elementRectangle.p1.y
    );
  });

  if (!interaction.isClicked) {
    const focusTarget = interaction.focusedElementList[0];

    switch (interaction.mode) {
      case InteractionMode.Translate:
        if (focusTarget.type === ElementType.Strategist) return;

        const anchorPointList = getCenterPointListFromFourSide(
          getRectangleFromElement(focusTarget)
        );
        anchorPointList.forEach((point) => {
          context.strokeStyle = "black";
          context.lineWidth = PARAM_RENDER.elementPointLineWidth;
          context.beginPath();
          context.arc(
            point.x,
            point.y,
            PARAM_ELEMENT.elementPointRadius,
            0,
            2 * Math.PI
          );
          context.stroke();
        });
        break;

      case InteractionMode.Connect:
        const mousePosition: Point = interaction.currentMousePosition;
        const closestAnchorPoint = findClosestPointFromPointList(
          mousePosition,
          getCenterPointListFromFourSide(getRectangleFromElement(focusTarget))
        );

        context.strokeStyle = "black";
        context.beginPath();
        context.arc(
          closestAnchorPoint.x,
          closestAnchorPoint.y,
          PARAM_ELEMENT.elementPointRadius,
          0,
          2 * Math.PI
        );
        context.fill();
        context.stroke();
    }
  }

  if (interaction.isClicked) {
    switch (interaction.mode) {
      case InteractionMode.Connect:
        context.strokeStyle = "black";
        context.lineWidth = 2;
        context.beginPath();
        context.moveTo(
          interaction.clickedSelectionRectangle.p1.x,
          interaction.clickedSelectionRectangle.p1.y
        );
        context.lineTo(
          interaction.clickedSelectionRectangle.p2.x,
          interaction.clickedSelectionRectangle.p2.y
        );
        context.stroke();

        const connectTargetStrategist = interaction.focusedElementList[1];
        if (connectTargetStrategist) {
          if (connectTargetStrategist.type !== ElementType.Strategist) return;

          const connectTargetRectangle = getRectangleFromElement(
            connectTargetStrategist
          );

          context.strokeStyle = PARAM_COLOR.connectTarget;
          context.lineWidth = PARAM_RENDER.focusThickness;
          context.strokeRect(
            connectTargetRectangle.p1.x,
            connectTargetRectangle.p1.y,
            connectTargetRectangle.p2.x - connectTargetRectangle.p1.x,
            connectTargetRectangle.p2.y - connectTargetRectangle.p1.y
          );
          const pinPointList: Array<Point> = convertPinDateListToPointList(
            connectTargetStrategist
          );
          context.strokeStyle = "black";
          pinPointList.forEach((point) => {
            context.beginPath();
            context.arc(
              point.x,
              point.y,
              PARAM_ELEMENT.elementPointRadius,
              0,
              2 * Math.PI
            );
            context.stroke();
          });

          const dockablePoint = pinPointList.find(
            (point) =>
              computeDistanceBetweenPoints(
                point,
                interaction.currentMousePosition
              ) < PARAM_ELEMENT.elementPointRadius
          );
          if (dockablePoint) {
            context.beginPath();
            context.arc(
              dockablePoint.x,
              dockablePoint.y,
              PARAM_ELEMENT.elementPointRadius,
              0,
              2 * Math.PI
            );
            context.fill();
          }
        }
    }
  }
};

export const renderStrategy = (
  context: CanvasRenderingContext2D | null,
  strategy: Strategy
) => {
  if (!context) return;
  strategy.strategistList.forEach((strategist) =>
    context.fillRect(
      strategist.x1,
      strategist.y1,
      strategist.x2 - strategist.x1,
      strategist.y2 - strategist.y1
    )
  );
};

export const renderFilterList = (
  context: CanvasRenderingContext2D | null,
  filterList: Array<Filter>
) => {
  if (!context) return;
  context.strokeStyle = "black";
  context.lineWidth = 2;

  filterList.forEach((filter) =>
    context.strokeRect(
      filter.x1,
      filter.y1,
      filter.x2 - filter.x1,
      filter.y2 - filter.y1
    )
  );
};

export const renderFilterApplicationList = (
  context: CanvasRenderingContext2D | null,
  filterApplicationList: Array<FilterApplication>
) => {
  if (!context) return;
  context.strokeStyle = "black";
  context.lineWidth = 2;
  filterApplicationList.forEach((filterApplication) => {
    context.beginPath();
    context.moveTo(filterApplication.x1, filterApplication.y1);
    context.lineTo(filterApplication.x2, filterApplication.y2);
    context.stroke();
  });
};
