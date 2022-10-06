import { configureStore, combineReducers } from "@reduxjs/toolkit";
import loginSlice from "./user";

const rootReducer = combineReducers({
  login: loginSlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
export type AppState = ReturnType<typeof rootReducer>;
export default store;
