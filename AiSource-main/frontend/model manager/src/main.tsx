import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Import defensive patches before anything else
import "./utils/errorOverlayPatch";

// Global error handler to prevent external scripts from breaking the app
window.addEventListener("error", (event) => {
  // Suppress errors from external scripts (like FullStory, browser extensions)
  if (
    event.filename &&
    (event.filename.includes("edge.fullstory.com") ||
      event.filename.includes("extension://") ||
      event.message?.includes("frame"))
  ) {
    console.debug("Suppressed external script error:", event.error);
    event.preventDefault();
    return false;
  }
});

// Handle unhandled promise rejections from external scripts
window.addEventListener("unhandledrejection", (event) => {
  if (
    event.reason?.message?.includes("frame") ||
    event.reason?.stack?.includes("fullstory")
  ) {
    console.debug(
      "Suppressed external script promise rejection:",
      event.reason,
    );
    event.preventDefault();
    return false;
  }
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
