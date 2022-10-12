import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";

export interface Segment {
  dateStart: Date;
  dateEnd: Date;
}

export interface Strategist {
  from_date: Date;
  to_date: Date;
  name: String;
  segmentList: Array<Segment>;
  id: number;
}

export interface Strategy {
  strategistList: Array<Strategist>;
}

const initialStrategy: Strategy = {
  strategistList: [],
};

export const fetchStrategy = createAsyncThunk<
  Array<{
    from_date: Date;
    to_date: Date;
    name: String;
  }>,
  string,
  { rejectValue: string }
>("fetchStrategy", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/api/strategist/get_strategist_list",
      config
    );
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
      state.strategistList = action.payload.map((item, index) => ({
        from_date: item.from_date,
        to_date: item.to_date,
        name: item.name,
        segmentList: [],
        id: index,
      }));
    });
    builder.addCase(fetchStrategy.rejected, (state, action) => {
      state.strategistList = [];
    });
  },
});

export default strategySlice;
