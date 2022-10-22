export enum ElementType {
  Strategist = "Strategist",
  Filter = "Filter",
}


export interface Segment {
  dateStart: Date;
  dateEnd: Date;
}

export interface Strategist {
  type: ElementType.Strategist
  id?: number;
  dateStart: Date;
  dateEnd: Date;
  name: String;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Filter {
  type: ElementType.Filter
  id?: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Strategy {
  strategistList: Array<Strategist>;
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
  Idle = "Idle",
  Create = "Create",
  Translate = "Translate",
  Reshape = "Reshape",
  Connect = "Connect",
}

export enum RectangleFocusRegion {
  Inner,
  Edge,
  Corner,
  Outer,
}

export interface UserInteraction {
  clickedSelectionRectangle: Rectangle;
  whileClick: boolean;
  mode: InteractionMode;
  createTarget: ElementType;
  focusTarget?: Strategist | Filter;
  currentMousePosition: Point;
}
