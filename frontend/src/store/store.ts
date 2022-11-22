import { configureStore, combineReducers } from "@reduxjs/toolkit";
import loginSlice from "./login";
import timelineSlice from "./timeline";
import interactionSlice from "./interaction";
import screenerSlice from "./screener";
import screenerApplication from "./screenerApplication";
import segmentSlice from "./segment";

const rootReducer = combineReducers({
  login: loginSlice.reducer,
  timeline: timelineSlice.reducer,
  screener: screenerSlice.reducer,
  segment: segmentSlice.reducer,
  screenerApplication: screenerApplication.reducer,
  interaction: interactionSlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type AppDispatch = typeof store.dispatch;
export type AppState = ReturnType<typeof rootReducer>;
export default store;
