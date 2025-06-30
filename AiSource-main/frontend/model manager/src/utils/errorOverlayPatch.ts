/**
 * Defensive patch for Vite ErrorOverlay conflicts with external scripts
 */

// Store the original fetch before external scripts can override it
const originalFetch = window.fetch.bind(window);

// Create an isolated fetch function that bypasses external script interference
export const isolatedFetch = (
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> => {
  return originalFetch(input, init);
};

// Patch potential undefined frame access issues
(() => {
  // Store original methods before external scripts can override them
  const originalAddEventListener = EventTarget.prototype.addEventListener;
  const originalRemoveEventListener = EventTarget.prototype.removeEventListener;

  // Defensive patching for iframe-related operations
  if (typeof window !== "undefined") {
    const originalCreateElement = document.createElement.bind(document);

    document.createElement = function (
      tagName: string,
      options?: ElementCreationOptions,
    ) {
      const element = originalCreateElement(tagName, options);

      // Add defensive properties for iframe elements
      if (tagName.toLowerCase() === "iframe") {
        try {
          Object.defineProperty(element, "frame", {
            get() {
              return this.contentWindow || {};
            },
            configurable: true,
          });
        } catch (e) {
          // Silently fail if we can't add the property
        }
      }

      return element;
    };

    // Defensive error boundary for ErrorOverlay
    const originalErrorOverlay = (window as any).ErrorOverlay;
    if (originalErrorOverlay) {
      (window as any).ErrorOverlay = function (...args: any[]) {
        try {
          return new originalErrorOverlay(...args);
        } catch (error) {
          console.debug("ErrorOverlay creation failed, using fallback:", error);
          // Return a minimal mock object to prevent further errors
          return {
            show: () => {},
            hide: () => {},
            dispose: () => {},
          };
        }
      };
    }
  }
})();

export {};
