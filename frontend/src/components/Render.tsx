import {
  ElementType,
  Screener,
  ScreenerApplication,
  InteractionMode,
  Point,
  TimeLineList,
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
        if (focusTarget.type === ElementType.Timeline) return;

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
      case InteractionMode.Idle:
        context.strokeStyle = PARAM_COLOR.focus;
        const selectionRectangle = interaction.clickedSelectionRectangle;
        context.lineWidth = 1.0;
        context.strokeRect(
          selectionRectangle.p1.x,
          selectionRectangle.p1.y,
          selectionRectangle.p2.x - selectionRectangle.p1.x,
          selectionRectangle.p2.y - selectionRectangle.p1.y
        );
        break;
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

        const connectTargetTimeline = interaction.focusedElementList[1];
        if (connectTargetTimeline) {
          if (connectTargetTimeline.type !== ElementType.Timeline) return;

          const connectTargetRectangle = getRectangleFromElement(
            connectTargetTimeline
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
            connectTargetTimeline
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
        break;
      case InteractionMode.Create:
        context.strokeStyle = "black";
        const creationRectangle = interaction.clickedSelectionRectangle;
        context.lineWidth = 1.0;
        context.strokeRect(
          creationRectangle.p1.x,
          creationRectangle.p1.y,
          creationRectangle.p2.x - creationRectangle.p1.x,
          creationRectangle.p2.y - creationRectangle.p1.y
        );
        break;
    }
  }
};

export const renderTimelineList = (
  context: CanvasRenderingContext2D | null,
  timelineList: TimeLineList
) => {
  if (!context) return;
  timelineList.timelineList.forEach((timeline) =>
    context.fillRect(
      timeline.x1,
      timeline.y1,
      timeline.x2 - timeline.x1,
      timeline.y2 - timeline.y1
    )
  );
};

export const renderScreenerList = (
  context: CanvasRenderingContext2D | null,
  screenerList: Array<Screener>
) => {
  if (!context) return;
  context.strokeStyle = "black";
  context.lineWidth = 2;

  screenerList.forEach((screener) =>
    context.strokeRect(
      screener.x1,
      screener.y1,
      screener.x2 - screener.x1,
      screener.y2 - screener.y1
    )
  );
};

export const renderScreenerApplicationList = (
  context: CanvasRenderingContext2D | null,
  screenerApplicationList: Array<ScreenerApplication>
) => {
  if (!context) return;
  context.strokeStyle = "black";
  context.lineWidth = 2;
  screenerApplicationList.forEach((screenerApplication) => {
    context.beginPath();
    context.moveTo(screenerApplication.x1, screenerApplication.y1);
    context.lineTo(screenerApplication.x2, screenerApplication.y2);
    context.stroke();
  });
};
