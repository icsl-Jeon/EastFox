import {
  Filter,
  InteractionMode,
  Strategy,
  UserInteraction,
} from "../types/type";
import { PARAMETERS } from "../types/constant";

export const renderInteraction = (
  context: CanvasRenderingContext2D | null,
  interaction: UserInteraction
) => {
  if (!context) return;
  if (!interaction.whileClick) {
    switch (interaction.mode) {
      case InteractionMode.Translate:
        if (!interaction.focusTarget) return;
        context.strokeStyle = "#7bd4ed";
        context.lineWidth = PARAMETERS.renderHoverModeTranslateThickness;
        const margin = PARAMETERS.renderHoverModeTranslateMargin;
        const focusTarget = interaction.focusTarget;
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
        break;
    }
  }

  if (interaction.whileClick) {
    context.globalAlpha = 0.2;
    context.fillRect(
      interaction.selectionRectangle.p1.x,
      interaction.selectionRectangle.p1.y,
      interaction.selectionRectangle.p2.x - interaction.selectionRectangle.p1.x,
      interaction.selectionRectangle.p2.y - interaction.selectionRectangle.p1.y
    );
    context.globalAlpha = 1;
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
  filter_list.forEach((filter) =>
    context.fillRect(
      filter.x1,
      filter.y1,
      filter.x2 - filter.x1,
      filter.y2 - filter.y1
    )
  );
};
