import { configureStore, combineReducers } from "@reduxjs/toolkit";
import loginSlice from "./login";
import strategySlice from "./strategy";
import interactionSlice from "./interaction";
import filterSlice from "./filter";
import filterApplication from "./filterApplication";
import segmentSlice from "./segment";

const rootReducer = combineReducers({
  login: loginSlice.reducer,
  strategy: strategySlice.reducer,
  filter: filterSlice.reducer,
  segment: segmentSlice.reducer,
  filterApplication: filterApplication.reducer,
  interaction: interactionSlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
export type AppState = ReturnType<typeof rootReducer>;
export default store;
