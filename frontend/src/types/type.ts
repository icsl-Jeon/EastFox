export enum ElementType {
  Timeline = "Timeline",
  Screener = "Screener",
  ScreenerApplication = "ScreenerApplication",
}

export interface Timeline {
  type: ElementType.Timeline;
  id?: number;
  dateStart: string;
  dateEnd: string;
  name: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  pinDateList: Array<string>;
}

export interface Screener {
  type: ElementType.Screener;
  id?: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface TimeLineList {
  timelineList: Array<Timeline>;
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
  EdgeCenter,
  Corner,
  Outer,
}

export interface UserInteraction {
  clickedSelectionRectangle: Rectangle;
  isClicked: boolean;
  mode: InteractionMode;
  createElementType: ElementType;
  focusedElementList: Array<Timeline | Screener>;
  currentMousePosition: Point;
}

export interface ScreenerApplication {
  type: ElementType.ScreenerApplication;
  id?: number;
  screenerId: number;
  timelineId: number;
  appliedDate: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Segment {
  timelineId: number;
  dateStart: string;
  dateEnd: string;
  assetList: Array<string>;
}
