import {
  ElementType,
  Filter,
  InteractionMode,
  Point,
  Strategist,
  Strategy,
  UserInteraction,
} from "../types/type";
import { PARAMETERS } from "../types/constant";

const convertPinDateListToPointList = (strategist: Strategist) => {
  const dateStart = new Date(strategist.dateStart);
  const dateEnd = new Date(strategist.dateEnd);
  const pinPointList = strategist.pinDateList.map((date) => {
    const pinDate = new Date(date);
    const timeDifference = pinDate.valueOf() - dateStart.valueOf();
    const maxTimeDifference = dateEnd.valueOf() - dateStart.valueOf();
    return {
      x:
        strategist.x1 +
        (timeDifference / maxTimeDifference) * (strategist.x2 - strategist.x1),
      y: 0.5 * (strategist.y1 + strategist.y2),
    };
  });
  return pinPointList;
};

const computeDistanceBetweenPoints = (point1: Point, point2: Point) => {
  return Math.sqrt(
    Math.pow(point1.x - point2.x, 2) + Math.pow(point1.y - point2.y, 2)
  );
};

export const renderInteraction = (
  context: CanvasRenderingContext2D | null,
  interaction: UserInteraction
) => {
  if (!context) return;
  if (!interaction.whileClick) {
    const focusTarget = interaction.focusTargetList[0];
    let anchorPointList: Array<Point> = [];
    if (focusTarget)
      anchorPointList = [
        { x: focusTarget.x1, y: 0.5 * (focusTarget.y1 + focusTarget.y2) },
        { x: focusTarget.x2, y: 0.5 * (focusTarget.y1 + focusTarget.y2) },
        { x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y1 },
        { x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y2 },
      ];
    switch (interaction.mode) {
      case InteractionMode.Translate:
        if (!focusTarget) return;
        context.strokeStyle = "#7bd4ed";
        context.lineWidth = PARAMETERS.focusHighlightRectangleThickness;
        const margin = PARAMETERS.focusHighlightRectangleMargin;
        const p1 = {
          x: Math.min(focusTarget.x1, focusTarget.x2),
          y: Math.min(focusTarget.y1, focusTarget.y2),
        };
        const p2 = {
          x: Math.max(focusTarget.x1, focusTarget.x2),
          y: Math.max(focusTarget.y1, focusTarget.y2),
        };
        context.strokeRect(
          p1.x - margin,
          p1.y - margin,
          p2.x - p1.x + 2 * margin,
          p2.y - p1.y + 2 * margin
        );
        if (focusTarget.type === ElementType.Strategist) return;

        context.strokeStyle = "orange";
        anchorPointList.forEach((point) => {
          context.lineWidth = 2;
          context.beginPath();
          context.arc(
            point.x,
            point.y,
            PARAMETERS.dockingRadius,
            0,
            2 * Math.PI
          );
          context.stroke();
        });
        break;

      case InteractionMode.Connect:
        context.strokeStyle = "orange";
        const mousePosition: Point = interaction.currentMousePosition;
        const distanceToAnchorPointList = anchorPointList.map(
          (point) =>
            Math.pow(mousePosition.x - point.x, 2) +
            Math.pow(mousePosition.y - point.y, 2)
        );
        const minDistance = Math.min(...distanceToAnchorPointList);
        const closestAnchorPoint =
          anchorPointList[distanceToAnchorPointList.indexOf(minDistance)];
        context.lineWidth = 3;
        context.beginPath();
        context.arc(
          closestAnchorPoint.x,
          closestAnchorPoint.y,
          PARAMETERS.dockingRadius,
          0,
          2 * Math.PI
        );
        context.fill();
        context.stroke();
    }
  }

  if (interaction.whileClick) {
    switch (interaction.mode) {
      case InteractionMode.Create:
        context.globalAlpha = 0.2;
        context.fillRect(
          interaction.clickedSelectionRectangle.p1.x,
          interaction.clickedSelectionRectangle.p1.y,
          interaction.clickedSelectionRectangle.p2.x -
            interaction.clickedSelectionRectangle.p1.x,
          interaction.clickedSelectionRectangle.p2.y -
            interaction.clickedSelectionRectangle.p1.y
        );
        context.globalAlpha = 1;
        break;

      case InteractionMode.Connect:
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
        const focusTarget = interaction.focusTargetList[1];

        if (focusTarget) {
          if (focusTarget.type !== ElementType.Strategist) return;
          context.strokeStyle = "#ebaf60";
          context.lineWidth = PARAMETERS.focusHighlightRectangleThickness;
          const margin = PARAMETERS.strategyConnectMargin;
          const p1 = {
            x: Math.min(focusTarget.x1, focusTarget.x2),
            y: Math.min(focusTarget.y1, focusTarget.y2),
          };
          const p2 = {
            x: Math.max(focusTarget.x1, focusTarget.x2),
            y: Math.max(focusTarget.y1, focusTarget.y2),
          };
          context.strokeRect(
            p1.x - margin,
            p1.y - margin,
            p2.x - p1.x + 2 * margin,
            p2.y - p1.y + 2 * margin
          );
          const pinPointList: Array<Point> =
            convertPinDateListToPointList(focusTarget);
          pinPointList.forEach((point) => {
            context.beginPath();
            context.arc(
              point.x,
              point.y,
              PARAMETERS.dockingRadius,
              0,
              2 * Math.PI
            );
            context.stroke();
          });
          const dockablePoint = pinPointList.find(
            (point) =>
              computeDistanceBetweenPoints(
                point,
                interaction.clickedSelectionRectangle.p2
              ) < PARAMETERS.dockingRadius
          );
          if (dockablePoint) {
            context.beginPath();
            context.arc(
              dockablePoint.x,
              dockablePoint.y,
              PARAMETERS.dockingRadius,
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
  filter_list: Array<Filter>
) => {
  if (!context) return;
  context.strokeStyle = "black";
  context.lineWidth = 2;

  filter_list.forEach((filter) =>
    context.strokeRect(
      filter.x1,
      filter.y1,
      filter.x2 - filter.x1,
      filter.y2 - filter.y1
    )
  );
};
