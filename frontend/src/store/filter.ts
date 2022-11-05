import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { ElementType, Filter } from "../types/type";

const initialFilter = { filterList: Array<Filter>() };

export const getFilterList = createAsyncThunk<
  Array<{
    id: number;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  }>,
  string,
  { rejectValue: string }
>("getFilterList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/api/strategy/get_filter_list",
      config
    );
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch filter failed");
  }
});

export const addFilter = createAsyncThunk<
  {
    success: boolean;
    updatedFilter: Filter;
  },
  {
    accessToken: string;
    newFilter: Filter;
  },
  { rejectValue: string }
>("addFilter", async ({ newFilter, accessToken }, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": `application/x-www-form-urlencoded`,
      },
    };

    const body = {
      x1: newFilter.x1,
      y1: newFilter.y1,
      x2: newFilter.x2,
      y2: newFilter.y2,
    };

    const { data } = await axios.post(
      "http://127.0.0.1:8000/api/strategy/create_filter",
      body,
      config
    );
    const updatedFilter: Filter = {
      type: ElementType.Filter,
      id: data.id,
      x1: data.x1,
      y1: data.y1,
      x2: data.x2,
      y2: data.y2,
    };
    return { success: true, updatedFilter: updatedFilter };
  } catch (e) {
    return thunkAPI.rejectWithValue("Add Filter failed");
  }
});

const filterSlice = createSlice({
  name: "filter",
  initialState: initialFilter,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(getFilterList.fulfilled, (state, action) => {
      state.filterList = action.payload.map((item) => ({
        type: ElementType.Filter,
        id: item.id,
        x1: item.x1,
        x2: item.x2,
        y1: item.y1,
        y2: item.y2,
      }));
    });
    builder.addCase(getFilterList.rejected, (state, action) => {
      state.filterList = [];
    });
    builder.addCase(addFilter.fulfilled, (state, action) => {
      state.filterList.push(action.payload.updatedFilter);
    });
    builder.addCase(addFilter.rejected, (state, action) => {});
  },
});

export default filterSlice;
