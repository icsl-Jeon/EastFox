import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { ElementType, Screener } from "../types/type";

const initialScreener = { screenerList: Array<Screener>() };

export const readScreenerList = createAsyncThunk<
  Array<Screener>,
  string,
  { rejectValue: string }
>("readScreenerList", async (accessToken, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
    const { data } = await axios.get(
      "http://127.0.0.1:8000/interface/read/screener_list",
      config
    );

    return data.map(
      (item: {
        id: number;
        x1: number;
        y1: number;
        x2: number;
        y2: number;
      }) => ({
        type: ElementType.Screener,
        id: item.id,
        x1: item.x1,
        x2: item.x2,
        y1: item.y1,
        y2: item.y2,
      })
    );
  } catch (e) {
    return thunkAPI.rejectWithValue("Read screener list failed");
  }
});

export const createScreener = createAsyncThunk<
  {
    success: boolean;
    createdScreener: Screener;
  },
  {
    accessToken: string;
    newScreener: Screener;
  },
  { rejectValue: string }
>("createScreener", async ({ newScreener, accessToken }, thunkAPI) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": `application/x-www-form-urlencoded`,
      },
    };

    const requestBody = {
      x1: newScreener.x1,
      y1: newScreener.y1,
      x2: newScreener.x2,
      y2: newScreener.y2,
    };

    const { data } = await axios.post(
      "http://127.0.0.1:8000/interface/create/screener",
      requestBody,
      config
    );
    const createdScreener: Screener = {
      type: ElementType.Screener,
      id: data.id,
      x1: data.x1,
      y1: data.y1,
      x2: data.x2,
      y2: data.y2,
    };
    return { success: true, createdScreener: createdScreener };
  } catch (e) {
    return thunkAPI.rejectWithValue("Create screener failed");
  }
});

const screenerSlice = createSlice({
  name: "screener",
  initialState: initialScreener,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(readScreenerList.fulfilled, (state, action) => {
      state.screenerList = action.payload;
    });
    builder.addCase(readScreenerList.rejected, (state, action) => {
      state.screenerList = [];
    });
    builder.addCase(createScreener.fulfilled, (state, action) => {
      state.screenerList.push(action.payload.createdScreener);
    });
    builder.addCase(createScreener.rejected, (state, action) => {});
  },
});

export default screenerSlice;
