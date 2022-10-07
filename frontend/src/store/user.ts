import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import axios, { AxiosError } from "axios";

export interface LoginStatus {
  status: "idle" | "pending" | "succeeded" | "failed";
  userInfo: { name: string; access_token: string };
  errorMessage: string;
}

interface LoginActionPayload {
  email: string;
  name: string;
  access: string;
}

export const fetchUserByLogin = createAsyncThunk<
  LoginActionPayload,
  object,
  { rejectValue: string }
>("fetchUserByLogin", async (loginInfo, thunkAPI) => {
  try {
    const { data } = await axios.post(
      "http://127.0.0.1:8000/user/login",
      loginInfo
    );
    return data;
  } catch (e) {
    return thunkAPI.rejectWithValue("Login failed");
  }
});

// TODO(@): consider localStorage
const initialLogin: LoginStatus = {
  status: "idle",
  userInfo: { name: "", access_token: "" },
  errorMessage: "",
};
const loginSlice = createSlice({
  name: "login",
  initialState: initialLogin,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchUserByLogin.fulfilled, (state, action) => {
      state.status = "succeeded";
      state.userInfo.name = action.payload.name;
      state.userInfo.access_token = action.payload.access;
    });
    builder.addCase(fetchUserByLogin.pending, (state) => {
      state.status = "pending";
    });
    builder.addCase(fetchUserByLogin.rejected, (state, action) => {
      console.log(action.payload);
      state.status = "failed";
      if (action.payload) {
        state.errorMessage = action.payload;
      } else {
        state.errorMessage = "Unknown error";
      }
    });
  },
});

export default loginSlice;
