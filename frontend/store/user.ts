import {createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios from 'axios'

export interface LoginStatus {
  status: 'idle' | 'pending' | 'succeeded' | 'failed',
  userInfo: { name: string }
}

const fetchUserByLogin = createAsyncThunk(
  'fetchUserByLogin',
  async (loginInfo: { username: string, password: string }, thunkAPI) => {
    const config = {
      headers: {
        'Content-type': 'application/json'
      }
    }
    try {
      const {data} = await axios.post(
        '/api/users/login/',
        {'username': loginInfo.username, 'password': loginInfo.password},
        config
      )
      return data;
    } catch (e) {
      return thunkAPI.rejectWithValue(await e.response.data)
    }
  }
)

// TODO(@): consider localStorage
const initialLogin: LoginStatus = {status: 'idle', userInfo: {name: ""}}
const login = createSlice({
    name: "login",
    initialState: initialLogin,
    reducers: {},
    extraReducers: (builder) => {
      builder.addCase(fetchUserByLogin.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.userInfo.name = action.payload.username
      })
    }
  }
)