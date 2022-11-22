import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { ElementType, ScreenerApplication } from "../types/type";

const initialScreenerApplication = {
  screenerApplicationList: Array<ScreenerApplication>(),
};

export const readScreenerApplicationList = createAsyncThunk<
  Array<ScreenerApplication>,
  string,
  { rejectValue: string }
>("readScreenerApplicationList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/interface/read/screener_application_list",
      config
    );
    console.log(data);
    return data.map(
      (item: {
        id: number;
        screener: number;
        timeline: number;
        applied_date: string;
        x1: number;
        y1: number;
        x2: number;
        y2: number;
      }) => ({
        type: ElementType.ScreenerApplication,
        id: item.id,
        screenerId: item.screener,
        timelineId: item.timeline,
        appliedDate: item.applied_date,
        x1: item.x1,
        x2: item.x2,
        y1: item.y1,
        y2: item.y2,
      })
    );
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch filter application failed");
  }
});

export const createScreenerApplication = createAsyncThunk<
  {
    success: boolean;
    createdFilterApplication: ScreenerApplication;
  },
  {
    accessToken: string;
    newScreenerApplication: ScreenerApplication;
  },
  { rejectValue: string }
>(
  "createScreenerApplication",
  async ({ newScreenerApplication, accessToken }, thunkAPI) => {
    try {
      const config = {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": `application/x-www-form-urlencoded`,
        },
      };

      const reqeustBody = {
        screener_id: newScreenerApplication.screenerId,
        timeline_id: newScreenerApplication.timelineId,
        applied_date: newScreenerApplication.appliedDate,
        x1: newScreenerApplication.x1,
        y1: newScreenerApplication.y1,
        x2: newScreenerApplication.x2,
        y2: newScreenerApplication.y2,
      };

      const { data } = await axios.post(
        "http://127.0.0.1:8000/interface/create/screener_application",
        reqeustBody,
        config
      );
      const createdFilterApplication: ScreenerApplication = {
        type: ElementType.ScreenerApplication,
        id: data.id,
        screenerId: data.screener,
        timelineId: data.timeline,
        appliedDate: data.applied_date,
        x1: data.x1,
        y1: data.y1,
        x2: data.x2,
        y2: data.y2,
      };
      return {
        success: true,
        createdFilterApplication: createdFilterApplication,
      };
    } catch (e) {
      return thunkAPI.rejectWithValue("Create screener application failed");
    }
  }
);

const screenerApplication = createSlice({
  name: "screenerApplication",
  initialState: initialScreenerApplication,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(readScreenerApplicationList.fulfilled, (state, action) => {
      state.screenerApplicationList = action.payload;
    });
    builder.addCase(readScreenerApplicationList.rejected, (state, action) => {
      state.screenerApplicationList = [];
    });
    builder.addCase(createScreenerApplication.fulfilled, (state, action) => {
      // state.screenerApplicationList.push(
      //   action.payload.createdFilterApplication
      // );
    });
    builder.addCase(createScreenerApplication.rejected, (state, action) => {});
  },
});

export default screenerApplication;
