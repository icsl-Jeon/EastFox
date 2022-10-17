import { configureStore, combineReducers } from "@reduxjs/toolkit";
import loginSlice from "./login";
import strategySlice from "./strategy";
import interactionSlice from "./interaction";

const rootReducer = combineReducers({
  login: loginSlice.reducer,
  strategy: strategySlice.reducer,
  interaction: interactionSlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
export type AppState = ReturnType<typeof rootReducer>;
export default store;
