import { Strategist } from "../store/strategy";

export const PARAMETERS = {
  elementDistributionOffsetY: 100,
  canvasHeight: 500,
};

export enum CanvasElementType {
  Strategist,
  Filter,
}

export interface Point {
  x: number;
  y: number;
}

export enum InteractionMode {
  Create,
  Select,
}

export class UserInteraction {
  lastClickedPoint: Point;
  whileClick: boolean;
  mode: InteractionMode;
  createTarget: CanvasElementType;

  constructor() {
    this.whileClick = false;
    this.lastClickedPoint = { x: 0, y: 0 };
    this.mode = InteractionMode.Create;
    this.createTarget = CanvasElementType.Strategist;
  }
}

export function addTwoPoints(p1: Point, p2: Point): Point {
  return { x: p1.x + p2.x, y: p1.y + p2.y };
}

interface Rectangle {
  isActive: boolean;
  p1: Point;
  p2: Point;
}

export default class CanvasElement {
  id: number;
  type: CanvasElementType;
  rectangle: Rectangle;

  constructor(id?: number, type?: CanvasElementType) {
    this.id = 0;
    this.type = CanvasElementType.Strategist;
    this.rectangle = {
      isActive: false,
      p1: { x: 0, y: 0 },
      p2: { x: 0, y: 0 },
    };

    if (id) this.id = id;
    if (type) this.type = type;
  }

  draw(context: CanvasRenderingContext2D) {
    if (this.rectangle.isActive)
      context.fillRect(
        this.rectangle.p1.x,
        this.rectangle.p1.y,
        this.rectangle.p2.x - this.rectangle.p1.x,
        this.rectangle.p2.y - this.rectangle.p1.y
      );
  }
}
