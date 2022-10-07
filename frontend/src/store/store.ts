import { configureStore, combineReducers } from "@reduxjs/toolkit";
import loginSlice from "./user";
import strategySlice from "./strategy";

const rootReducer = combineReducers({
  login: loginSlice.reducer,
  strategy: strategySlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
export type AppState = ReturnType<typeof rootReducer>;
export default store;
