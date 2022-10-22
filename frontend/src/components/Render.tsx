import {
  ElementType,
  Filter,
  InteractionMode,
  Point,
  Strategy,
  UserInteraction,
} from "../types/type";
import {PARAMETERS} from "../types/constant";

export const renderInteraction = (
  context: CanvasRenderingContext2D | null,
  interaction: UserInteraction
) => {
  if (!context) return;
  if (!interaction.whileClick) {
    const focusTarget = interaction.focusTarget;
    let connectAnchorPointList: Array<Point> = []
    if (focusTarget)
      connectAnchorPointList = [
        {x: focusTarget.x1, y: 0.5 * (focusTarget.y1 + focusTarget.y2)},
        {x: focusTarget.x2, y: 0.5 * (focusTarget.y1 + focusTarget.y2)},
        {x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y1},
        {x: 0.5 * (focusTarget.x1 + focusTarget.x2), y: focusTarget.y2},
      ]
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
        connectAnchorPointList.forEach(point => {
          context.lineWidth = 2
          context.beginPath();
          context.arc(point.x, point.y, PARAMETERS.focusEdgeThickness, 0, 2 * Math.PI)
          context.stroke()
        })
        break;

      case InteractionMode.Connect:
        if (!interaction.focusTarget) return;
        if (interaction.focusTarget.type === ElementType.Strategist) return;
        context.strokeStyle = "orange";
        const point: Point = interaction.currentMousePosition
        context.lineWidth = 3
        context.beginPath();
        context.arc(point.x, point.y, PARAMETERS.focusEdgeThickness, 0, 2 * Math.PI)
        context.fill()
        context.stroke()

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
        break
      case InteractionMode.Connect:
        context.beginPath()
        context.moveTo(interaction.clickedSelectionRectangle.p1.x, interaction.clickedSelectionRectangle.p1.y)
        context.lineTo(interaction.clickedSelectionRectangle.p2.x, interaction.clickedSelectionRectangle.p2.y)
        context.stroke()
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
  context.strokeStyle = "black"
  context.lineWidth = 2

  filter_list.forEach((filter) =>
    context.strokeRect(
      filter.x1,
      filter.y1,
      filter.x2 - filter.x1,
      filter.y2 - filter.y1
    )
  );
};
