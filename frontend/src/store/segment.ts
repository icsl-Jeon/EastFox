import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { Segment } from "../types/type";

const initialSegmentList = { segmentList: Array<Segment>() };

export const getSegmentList = createAsyncThunk<
  Array<{
    strategist: number;
    asset_list: Array<string>;
    from_date: string;
    to_date: string;
  }>,
  string,
  { rejectValue: string }
>("getSegmentList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/api/strategy/get_segment_list",
      config
    );
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch segment list failed");
  }
});

const segmentSlice = createSlice({
  name: "segment",
  initialState: initialSegmentList,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(getSegmentList.fulfilled, (state, action) => {
      state.segmentList = action.payload.map((item) => ({
        strategistId: item.strategist,
        dateStart: item.from_date,
        dateEnd: item.to_date,
        assetList: item.asset_list,
      }));
    });
    builder.addCase(getSegmentList.rejected, (state, action) => {
      state.segmentList = [];
    });
  },
});

export default segmentSlice;
