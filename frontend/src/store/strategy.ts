import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { Strategy, Strategist } from "../types/type";

const initialStrategy: Strategy = {
  strategistList: [],
};

export const fetchStrategy = createAsyncThunk<
  Array<{
    id: number;
    from_date: Date;
    to_date: Date;
    name: String;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
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
      "http://127.0.0.1:8000/api/strategy/get_strategist_list",
      config
    );
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch strategy failed");
  }
});

export const addStrategist = createAsyncThunk<
  {
    success: boolean;
    updatedStrategist: Strategist;
  },
  {
    accessToken: string;
    newStrategist: Strategist;
  },
  { rejectValue: string }
>("addStrategist", async ({ newStrategist, accessToken }, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": `application/x-www-form-urlencoded`,
      },
    };

    const body = {
      from_date: newStrategist.dateStart.toISOString().slice(0, 10),
      to_date: newStrategist.dateEnd.toISOString().slice(0, 10),
      name: newStrategist.name,
      x1: newStrategist.x1,
      y1: newStrategist.y1,
      x2: newStrategist.x2,
      y2: newStrategist.y2,
    };

    const { data } = await axios.post(
      "http://127.0.0.1:8000/api/strategy/create_strategist",
      body,
      config
    );

    return { success: true, updatedStrategist: data };
  } catch (e) {
    return thunkAPI.rejectWithValue("Add strategist failed");
  }
});

export const applyFilterToStrategist = createAsyncThunk<
  boolean,
  {
    filterId: number;
    strategistId: number;
  },
  { rejectValue: string }
>("applyFilterToStrategist", async ({ filterId, strategistId }, thunkAPI) => {
  try {
    return true;
  } catch (e) {
    return thunkAPI.rejectWithValue("Apply filter failed");
  }
});

const strategySlice = createSlice({
  name: "strategy",
  initialState: initialStrategy,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchStrategy.fulfilled, (state, action) => {
      state.strategistList = action.payload.map((item) => ({
        dateStart: item.from_date,
        dateEnd: item.to_date,
        name: item.name,
        id: item.id,
        x1: item.x1,
        x2: item.x2,
        y1: item.y1,
        y2: item.y2,
      }));
    });
    builder.addCase(fetchStrategy.rejected, (state, action) => {
      state.strategistList = [];
    });
    builder.addCase(addStrategist.fulfilled, (state, action) => {
      state.strategistList.push(action.payload.updatedStrategist);
    });
    builder.addCase(addStrategist.rejected, (state, action) => {});
  },
});

export default strategySlice;
