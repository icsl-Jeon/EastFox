import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { ElementType, Timeline } from "../types/type";

const initialTimeline = { timelineList: Array<Timeline>() };

export const readTimelineList = createAsyncThunk<
  Array<Timeline>,
  string,
  { rejectValue: string }
>("readTimelineList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/interface/read/timeline_list",
      config
    );

    return data.map(
      (item: {
        id: number;
        from_date: string;
        to_date: string;
        name: string;
        x1: number;
        y1: number;
        x2: number;
        y2: number;
      }) => ({
        type: ElementType.Timeline,
        dateStart: item.from_date,
        dateEnd: item.to_date,
        name: item.name,
        id: item.id,
        x1: item.x1,
        x2: item.x2,
        y1: item.y1,
        y2: item.y2,
        pinDateList: ["1990-01-01", "2010-01-01"],
      })
    );
  } catch (e) {
    return thunkAPI.rejectWithValue("Read timeline list failed");
  }
});

export const createTimeline = createAsyncThunk<
  {
    success: boolean;
    createdTimeline: Timeline;
  },
  {
    accessToken: string;
    newTimeline: Timeline;
  },
  { rejectValue: string }
>("createTimeline", async ({ accessToken, newTimeline }, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": `application/x-www-form-urlencoded`,
      },
    };

    const requestBody = {
      from_date: newTimeline.dateStart,
      to_date: newTimeline.dateEnd,
      name: newTimeline.name,
      x1: newTimeline.x1,
      y1: newTimeline.y1,
      x2: newTimeline.x2,
      y2: newTimeline.y2,
    };

    const { data } = await axios.post(
      "http://127.0.0.1:8000/interface/create/timeline",
      requestBody,
      config
    );
    const createdTimeline: Timeline = {
      type: ElementType.Timeline,
      id: data.id,
      dateStart: data.from_date,
      dateEnd: data.to_date,
      name: data.name,
      x1: data.x1,
      y1: data.y1,
      x2: data.x2,
      y2: data.y2,
      pinDateList: ["1990-01-01", "2010-01-01"],
    };
    return {
      success: true,
      createdTimeline: createdTimeline,
    };
  } catch (e) {
    return thunkAPI.rejectWithValue("Create timeline failed");
  }
});

const timelineSlice = createSlice({
  name: "timeline",
  initialState: initialTimeline,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(readTimelineList.fulfilled, (state, action) => {
      state.timelineList = action.payload;
    });
    builder.addCase(readTimelineList.rejected, (state, action) => {
      state.timelineList = [];
    });
    builder.addCase(createTimeline.fulfilled, (state, action) => {
      state.timelineList.push(action.payload.createdTimeline);
    });
    builder.addCase(createTimeline.rejected, (state, action) => {});
  },
});

export default timelineSlice;
