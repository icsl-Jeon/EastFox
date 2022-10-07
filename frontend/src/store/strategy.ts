import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";

export interface Segment {
  dateStart: Date;
  dateEnd: Date;
}

export interface Strategist {
  segmentList: Array<Segment>;
}

export interface Strategy {
  strategistList: Array<Strategist>;
}

const initialStrategy: Strategy = {
  strategistList: [],
};

export const fetchStrategy = createAsyncThunk<
  [],
  string,
  { rejectValue: string }
>("fetchStrategy", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    console.log(accessToken);
    const { data } = await axios.get(
      "http://127.0.0.1:8000/api/strategist/get_strategist_list",
      config
    );
    console.log(data);
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch strategy failed");
  }
});

const strategySlice = createSlice({
  name: "strategy",
  initialState: initialStrategy,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchStrategy.fulfilled, (state, action) => {
      state.strategistList = action.payload;
    });
    builder.addCase(fetchStrategy.rejected, (state, action) => {
      state.strategistList = [];
    });
  },
});

export default strategySlice;
