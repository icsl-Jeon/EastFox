import {
  ElementType,
  InteractionMode,
  Point,
  Rectangle,
  RectangleFocusRegion,
  Screener,
  ScreenerApplication,
  Timeline,
  UserInteraction,
} from "./type";
import { PARAM_ELEMENT } from "./constant";
import { MouseEvent } from "react";

export const convertPinDateListToPointList = (timeline: Timeline) => {
  const dateStart = new Date(timeline.dateStart);
  const dateEnd = new Date(timeline.dateEnd);
  return timeline.pinDateList.map((date) => {
    const pinDate = new Date(date);
    const timeDifference = pinDate.valueOf() - dateStart.valueOf();
    const maxTimeDifference = dateEnd.valueOf() - dateStart.valueOf();
    return {
      x:
        timeline.x1 +
        (timeDifference / maxTimeDifference) * (timeline.x2 - timeline.x1),
      y: 0.5 * (timeline.y1 + timeline.y2),
    };
  });
};

export const deriveTimelineFromInteraction = (interaction: UserInteraction) => {
  const timeline: Timeline = {
    type: ElementType.Timeline,
    dateStart: "1980-01-01",
    dateEnd: "2020-12-31",
    name: `${new Date().toLocaleDateString()}`,
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: interaction.clickedSelectionRectangle.p2.x,
    y2: interaction.clickedSelectionRectangle.p2.y,
    pinDateList: ["2000-01-01", "2010-01-01"],
  };
  if (timeline.x2 - timeline.x1 > PARAM_ELEMENT.minimumAreaForTimeline)
    return timeline;
  else return null;
};

export const deriveScreenerFromInteraction = (interaction: UserInteraction) => {
  const screener: Screener = {
    type: ElementType.Screener,
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: interaction.clickedSelectionRectangle.p2.x,
    y2: interaction.clickedSelectionRectangle.p2.y,
  };

  if (
    Math.abs((screener.x2 - screener.x1) * (screener.y2 - screener.y1)) >
    PARAM_ELEMENT.minimumAreaForScreener
  )
    return screener;
  else return null;
};

export const deriveScreenerApplicationFromInteraction = (
  interaction: UserInteraction
) => {
  const focusTargetList = interaction.focusedElementList;
  if (focusTargetList.length !== 2) return null;
  if (focusTargetList[1].type !== ElementType.Timeline) return null;
  const pinPointList: Array<Point> = convertPinDateListToPointList(
    focusTargetList[1]
  );
  const dockablePoint = pinPointList.find(
    (point) =>
      computeDistanceBetweenPoints(
        point,
        interaction.clickedSelectionRectangle.p2
      ) < PARAM_ELEMENT.elementPointRadius
  );
  if (!dockablePoint) return null;
  if (!focusTargetList[0].id || !focusTargetList[1].id) return null;
  const dockableIndex = pinPointList.indexOf(dockablePoint);
  const newScreenerApplication: ScreenerApplication = {
    type: ElementType.ScreenerApplication,
    screenerId: focusTargetList[0].id,
    timelineId: focusTargetList[1].id,
    appliedDate: focusTargetList[1].pinDateList[dockableIndex],
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: dockablePoint.x,
    y2: dockablePoint.y,
  };
  return newScreenerApplication;
};

export const checkInsideRectangle = (
  point: Point,
  rectangle: Rectangle,
  margin = 0
) => {
  if (
    point.x >= rectangle.p1.x - margin &&
    point.x <= rectangle.p2.x + margin &&
    point.y >= rectangle.p1.y - margin &&
    point.y <= rectangle.p2.y + margin
  )
    return true;
  return false;
};

export const computeDistanceBetweenPoints = (point1: Point, point2: Point) => {
  return Math.sqrt(
    Math.pow(point1.x - point2.x, 2) + Math.pow(point1.y - point2.y, 2)
  );
};

export const computeFocusRegion = (
  mousePosition: Point,
  rectangle: Rectangle
) => {
  const rectangleCenter: Point = {
    x: (rectangle.p1.x + rectangle.p2.x) / 2,
    y: (rectangle.p1.y + rectangle.p2.y) / 2,
  };
  const width = rectangle.p2.x - rectangle.p1.x;
  const height = rectangle.p2.y - rectangle.p1.y;

  const mousePositionWithRespectToCenter: Point = {
    x: Math.abs(mousePosition.x - rectangleCenter.x),
    y: Math.abs(mousePosition.y - rectangleCenter.y),
  };

  const cornerBoundaryRectangleWithRespectToCenter: Rectangle = {
    p1: {
      x: width / 2 - PARAM_ELEMENT.elementPointRadius,
      y: height / 2 - PARAM_ELEMENT.elementPointRadius,
    },
    p2: {
      x: width / 2 + PARAM_ELEMENT.elementPointRadius,
      y: height / 2 + PARAM_ELEMENT.elementPointRadius,
    },
  };

  if (
    checkInsideRectangle(
      mousePositionWithRespectToCenter,
      cornerBoundaryRectangleWithRespectToCenter
    )
  )
    return RectangleFocusRegion.Corner;

  if (
    computeDistanceBetweenPoints(
      {
        x: 0,
        y: height / 2,
      },
      mousePositionWithRespectToCenter
    ) < PARAM_ELEMENT.elementPointRadius ||
    computeDistanceBetweenPoints(
      {
        x: width / 2,
        y: 0,
      },
      mousePositionWithRespectToCenter
    ) < PARAM_ELEMENT.elementPointRadius
  )
    return RectangleFocusRegion.EdgeCenter;

  const innerRectangleWithRespectToCenter: Rectangle = {
    p1: {
      x: 0,
      y: 0,
    },
    p2: {
      x: width / 2 - PARAM_ELEMENT.elementEdgeThickness / 2,
      y: height / 2 - PARAM_ELEMENT.elementEdgeThickness / 2,
    },
  };
  if (
    checkInsideRectangle(
      mousePositionWithRespectToCenter,
      innerRectangleWithRespectToCenter
    )
  )
    return RectangleFocusRegion.Inner;

  if (
    mousePosition.x < rectangle.p1.x - PARAM_ELEMENT.elementEdgeThickness / 2 ||
    mousePosition.x > rectangle.p2.x + PARAM_ELEMENT.elementEdgeThickness / 2 ||
    mousePosition.y < rectangle.p1.y - PARAM_ELEMENT.elementEdgeThickness / 2 ||
    mousePosition.y > rectangle.p2.y + PARAM_ELEMENT.elementEdgeThickness / 2
  )
    return RectangleFocusRegion.Outer;

  return RectangleFocusRegion.Edge;
};

export const getRectangleFromElement = (element: Screener | Timeline) => {
  const rectangle: Rectangle = {
    p1: {
      x: Math.min(element.x1, element.x2),
      y: Math.min(element.y1, element.y2),
    },
    p2: {
      x: Math.max(element.x1, element.x2),
      y: Math.max(element.y1, element.y2),
    },
  };
  return rectangle;
};

export const getCenterPointListFromFourSide = (rectangle: Rectangle) => {
  const anchorPointList: Array<Point> = [
    {
      x: rectangle.p1.x,
      y: 0.5 * (rectangle.p1.y + rectangle.p2.y),
    },
    {
      x: rectangle.p2.x,
      y: 0.5 * (rectangle.p1.y + rectangle.p2.y),
    },
    {
      x: 0.5 * (rectangle.p1.x + rectangle.p2.x),
      y: rectangle.p1.y,
    },
    {
      x: 0.5 * (rectangle.p1.x + rectangle.p2.x),
      y: rectangle.p2.y,
    },
  ];
  return anchorPointList;
};

export const findClosestPointFromPointList = (
  queryPoint: Point,
  pointList: Array<Point>
) => {
  const distanceToAnchorPointList = pointList.map(
    (point) =>
      Math.pow(queryPoint.x - point.x, 2) + Math.pow(queryPoint.y - point.y, 2)
  );
  const minDistance = Math.min(...distanceToAnchorPointList);
  return pointList[distanceToAnchorPointList.indexOf(minDistance)];
};

export const deriveInteractionModeFromHoverMousePosition = (
  hoverMousePosition: Point,
  element: Screener | Timeline
) => {
  const elementRectangle = getRectangleFromElement(element);
  const focusRegion = computeFocusRegion(hoverMousePosition, elementRectangle);
  if (element.type === ElementType.Timeline) {
    switch (focusRegion) {
      case RectangleFocusRegion.Corner:
        return InteractionMode.Reshape;
      case RectangleFocusRegion.EdgeCenter:
      case RectangleFocusRegion.Edge:
      case RectangleFocusRegion.Inner:
        return InteractionMode.Translate;
      default:
        return InteractionMode.Idle;
    }
  } else if (element.type === ElementType.Screener) {
    switch (focusRegion) {
      case RectangleFocusRegion.Corner:
        return InteractionMode.Reshape;
      case RectangleFocusRegion.EdgeCenter:
        return InteractionMode.Connect;
      case RectangleFocusRegion.Edge:
        return InteractionMode.Reshape;
      case RectangleFocusRegion.Inner:
        return InteractionMode.Translate;
      default:
        return InteractionMode.Idle;
    }
  }
};

export const getCurrentMousePointOnCanvas = (
  event: MouseEvent<HTMLCanvasElement>,
  canvas: HTMLCanvasElement
) => {
  const { clientX, clientY } = event;
  const boundingRect = canvas.getBoundingClientRect();
  const pointOnCanvas: Point = {
    x: clientX - boundingRect.left,
    y: clientY - boundingRect.top,
  };
  return pointOnCanvas;
};
