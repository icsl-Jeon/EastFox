import { UserInteraction } from "../types/type";
import { Strategy } from "../types/type";

export const renderInteraction = (
  context: CanvasRenderingContext2D | null,
  interaction: UserInteraction
) => {
  if (!context) return;
  if (!interaction.whileClick) return;
  context.globalAlpha = 0.2;
  context.fillRect(
    interaction.selectionRectangle.p1.x,
    interaction.selectionRectangle.p1.y,
    interaction.selectionRectangle.p2.x - interaction.selectionRectangle.p1.x,
    interaction.selectionRectangle.p2.y - interaction.selectionRectangle.p1.y
  );
  context.globalAlpha = 1;
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
