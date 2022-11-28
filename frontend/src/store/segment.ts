import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { Segment } from "../types/type";

const initialSegmentList = { segmentList: Array<Segment>() };

export const readSegmentList = createAsyncThunk<
  Array<Segment>,
  string,
  { rejectValue: string }
>("readSegmentList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/interface/read/segment_list",
      config
    );
    return data.map(
      (item: {
        timeline: number;
        asset_list: Array<string>;
        from_date: string;
        to_date: string;
      }) => ({
        timelineId: item.timeline,
        dateStart: item.from_date,
        dateEnd: item.to_date,
        assetList: item.asset_list,
      })
    );
  } catch (e) {
    return thunkAPI.rejectWithValue("Read segment list failed");
  }
});

export const updateSegmentListForTimeline = createAsyncThunk<
  Array<Segment>,
  { accessToken: string; timelineId: number },
  { rejectValue: string }
>("updateSegmentListForTimeline", async (input, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${input.accessToken}`,
        "Content-Type": `application/x-www-form-urlencoded`,
      },
    };
    const body = { timeline_id: input.timelineId };
    const { data } = await axios.post(
      "http://127.0.0.1:8000/core/update_segment_list_for_timeline",
      body,
      config
    );

    return data.map(
      (item: {
        timeline: number;
        asset_list: Array<string>;
        from_date: string;
        to_date: string;
      }) => ({
        timelineId: item.timeline,
        dateStart: item.from_date,
        dateEnd: item.to_date,
        assetList: item.asset_list,
      })
    );
  } catch (e) {
    return thunkAPI.rejectWithValue("Calculate segment list failed");
  }
});

const segmentSlice = createSlice({
  name: "segment",
  initialState: initialSegmentList,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(readSegmentList.fulfilled, (state, action) => {
      state.segmentList = action.payload;
    });
    builder.addCase(readSegmentList.rejected, (state, action) => {
      state.segmentList = [];
    });
    builder.addCase(updateSegmentListForTimeline.fulfilled, (state, action) => {
      if (action.payload.length === 0) return;

      const segmentListTemp = state.segmentList.filter(
        (item) => item.timelineId !== action.payload[0].timelineId
      );
      action.payload.forEach((item) => segmentListTemp.push(item));
      state.segmentList = segmentListTemp;
    });
    builder.addCase(
      updateSegmentListForTimeline.rejected,
      (state, action) => {}
    );
  },
});

export default segmentSlice;
