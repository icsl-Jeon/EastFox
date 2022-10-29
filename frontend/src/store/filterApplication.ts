import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { FilterApplication } from "../types/type";

const initialFilterApplication = {
  filterApplicationList: Array<FilterApplication>(),
};

export const getFilterApplicationList = createAsyncThunk<
  Array<{
    filter: number;
    strategist: number;
    applied_date: string;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  }>,
  string,
  { rejectValue: string }
>("getFilterApplicationList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/api/strategy/get_filter_application_list",
      config
    );
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Fetch filter application failed");
  }
});

export const addFilterApplication = createAsyncThunk<
  {
    success: boolean;
    updatedFilterApplication: FilterApplication;
  },
  {
    accessToken: string;
    newFilterApplication: FilterApplication;
  },
  { rejectValue: string }
>(
  "addFilterApplication",
  async ({ newFilterApplication, accessToken }, thunkAPI) => {
    try {
      const config = {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": `application/x-www-form-urlencoded`,
        },
      };

      const body = {
        filter_id: newFilterApplication.filterId,
        strategist_id: newFilterApplication.strategistId,
        applied_date: newFilterApplication.appliedDate,
        x1: newFilterApplication.x1,
        y1: newFilterApplication.y1,
        x2: newFilterApplication.x2,
        y2: newFilterApplication.y2,
      };

      const { data } = await axios.post(
        "http://127.0.0.1:8000/api/strategy/register_filter_to_strategist",
        body,
        config
      );

      return { success: true, updatedFilterApplication: data };
    } catch (e) {
      return thunkAPI.rejectWithValue("Add Filter application failed");
    }
  }
);

const filterSlice = createSlice({
  name: "filterApplication",
  initialState: initialFilterApplication,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(getFilterApplicationList.fulfilled, (state, action) => {
      state.filterApplicationList = action.payload.map((element) => ({
        filterId: element.filter,
        strategistId: element.strategist,
        appliedDate: element.applied_date,
        x1: element.x1,
        y1: element.y1,
        x2: element.x2,
        y2: element.y2,
      }));
    });
    builder.addCase(getFilterApplicationList.rejected, (state, action) => {
      state.filterApplicationList = [];
    });
    builder.addCase(addFilterApplication.fulfilled, (state, action) => {
      state.filterApplicationList.push(action.payload.updatedFilterApplication);
    });
    builder.addCase(addFilterApplication.rejected, (state, action) => {});
  },
});

export default filterSlice;
