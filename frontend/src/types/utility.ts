import {
  ElementType,
  Filter,
  FilterApplication,
  Point,
  Strategist,
  UserInteraction,
} from "./type";
import { PARAMETERS } from "./constant";

export const convertPinDateListToPointList = (strategist: Strategist) => {
  const dateStart = new Date(strategist.dateStart);
  const dateEnd = new Date(strategist.dateEnd);
  return strategist.pinDateList.map((date) => {
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
};
export const computeDistanceBetweenPoints = (point1: Point, point2: Point) => {
  return Math.sqrt(
    Math.pow(point1.x - point2.x, 2) + Math.pow(point1.y - point2.y, 2)
  );
};

export const deriveStrategistFromInteraction = (
  interaction: UserInteraction
) => {
  const strategist: Strategist = {
    type: ElementType.Strategist,
    dateStart: "1980-01-01",
    dateEnd: "2020-12-31",
    name: `${new Date().toLocaleDateString()}`,
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: interaction.clickedSelectionRectangle.p2.x,
    y2: interaction.clickedSelectionRectangle.p2.y,
    pinDateList: ["2000-01-01", "2010-01-01"],
  };
  if (strategist.x2 - strategist.x1 > PARAMETERS.minimumAreaForStrategist)
    return strategist;
  else return null;
};

export const deriveFilterFromInteraction = (interaction: UserInteraction) => {
  const filter: Filter = {
    type: ElementType.Filter,
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: interaction.clickedSelectionRectangle.p2.x,
    y2: interaction.clickedSelectionRectangle.p2.y,
  };

  if (
    Math.abs((filter.x2 - filter.x1) * (filter.y2 - filter.y1)) >
    PARAMETERS.minimumAreaForFilter
  )
    return filter;
  else return null;
};

export const deriveFilterApplicationFromInteraction = (
  interaction: UserInteraction
) => {
  const focusTargetList = interaction.focusTargetList;
  if (focusTargetList.length !== 2) return null;
  if (focusTargetList[1].type !== ElementType.Strategist) return null;
  const pinPointList: Array<Point> = convertPinDateListToPointList(
    focusTargetList[1]
  );
  const dockablePoint = pinPointList.find(
    (point) =>
      computeDistanceBetweenPoints(
        point,
        interaction.clickedSelectionRectangle.p2
      ) < PARAMETERS.dockingRadius
  );
  if (!dockablePoint) return null;
  if (!focusTargetList[0].id || !focusTargetList[1].id) return null;
  const dockableIndex = pinPointList.indexOf(dockablePoint);
  const newFilterApplication: FilterApplication = {
    filterId: focusTargetList[0].id,
    strategistId: focusTargetList[1].id,
    appliedDate: focusTargetList[1].pinDateList[dockableIndex],
    x1: interaction.clickedSelectionRectangle.p1.x,
    y1: interaction.clickedSelectionRectangle.p1.y,
    x2: dockablePoint.x,
    y2: dockablePoint.y,
  };
  return newFilterApplication;
};
