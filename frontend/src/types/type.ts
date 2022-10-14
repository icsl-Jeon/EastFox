export interface Segment {
  dateStart: Date;
  dateEnd: Date;
}

export interface Strategist {
  dateStart: Date;
  dateEnd: Date;
  name: String;
  segmentList: Array<Segment>;
  id: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Strategy {
  strategistList: Array<Strategist>;
}

export enum ElementType {
  Strategist,
  Filter,
}

export interface Point {
  x: number;
  y: number;
}

export interface Rectangle {
  p1: Point;
  p2: Point;
}

export enum InteractionMode {
  Create,
  Select,
}

export interface UserInteraction {
  selectionRectangle: Rectangle;
  whileClick: boolean;
  mode: InteractionMode;
  createTarget: ElementType;
}
