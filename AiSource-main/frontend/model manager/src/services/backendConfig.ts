import { isolatedFetch } from "../utils/errorOverlayPatch";

// Cache for backend URL with TTL (10 minutes for better performance)
const BACKEND_URL_CACHE_TTL = 10 * 60 * 1000;
const DEFAULT_PORTS = [8002, 8000, 8080, 8081, 3000, 5000];
const FALLBACK_URL = "http://localhost:8080";

interface BackendUrlCache {
  url: string | null;
  lastChecked: number;
  isChecking: boolean;
  lastError: Error | null;
}

const backendUrlCache: BackendUrlCache = {
  url: null,
  lastChecked: 0,
  isChecking: false,
  lastError: null,
};

// Simple in-memory lock to prevent concurrent checks
let checkInProgress = false;

/**
 * Check if a URL is reachable with exponential backoff
 */
async function checkUrlReachable(
  url: string,
  options: { signal?: AbortSignal; timeout?: number } = {},
): Promise<boolean> {
  const timeout = options.timeout || 1000;

  // Early return if external signal is already aborted
  if (options.signal?.aborted) {
    return false;
  }

  return new Promise((resolve) => {
    const controller = new AbortController();
    let isResolved = false;
    let timeoutId: NodeJS.Timeout | undefined;

    const cleanup = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = undefined;
      }
    };

    const resolveOnce = (value: boolean) => {
      if (!isResolved) {
        isResolved = true;
        cleanup();
        resolve(value);
      }
    };

    // Handle external signal abortion
    const abortHandler = () => {
      controller.abort();
      resolveOnce(false);
    };

    if (options.signal) {
      if (options.signal.aborted) {
        resolveOnce(false);
        return;
      }
      options.signal.addEventListener("abort", abortHandler, { once: true });
    }

    // Set up timeout
    timeoutId = setTimeout(() => {
      controller.abort();
      resolveOnce(false);
    }, timeout);

    // Make the fetch request using isolated fetch to avoid external script interference
    isolatedFetch(`${url}/health`, {
      signal: controller.signal,
      headers: {
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
        Accept: "application/json",
      },
      mode: "cors",
    })
      .then(async (response) => {
        if (response.ok) {
          try {
            const data = await response.json();
            resolveOnce(data.status === "healthy");
          } catch {
            resolveOnce(response.status === 200);
          }
        } else {
          resolveOnce(false);
        }
      })
      .catch(() => {
        resolveOnce(false);
      });
  });
}

/**
 * Get the backend URL with caching and automatic discovery
 */
export const getBackendUrl = async (forceRefresh = false): Promise<string> => {
  const now = Date.now();

  // Return cached URL if it's still valid and not marked as failed
  if (
    !forceRefresh &&
    backendUrlCache.url &&
    now - backendUrlCache.lastChecked < BACKEND_URL_CACHE_TTL
  ) {
    return backendUrlCache.url;
  }

  // If we recently failed, don't retry too often (increased delay)
  if (backendUrlCache.lastError && now - backendUrlCache.lastChecked < 30000) {
    console.debug("Skipping backend check due to recent error");
    return FALLBACK_URL;
  }

  // Prevent concurrent checks
  if (checkInProgress) {
    if (backendUrlCache.url) return backendUrlCache.url;
    console.debug("Backend check already in progress, returning fallback");
    return FALLBACK_URL;
  }

  checkInProgress = true;
  backendUrlCache.isChecking = true;
  backendUrlCache.lastError = null;

  try {
    // Try to read from config file first
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1500);

      const response = await isolatedFetch("/backend_config.json", {
        cache: "no-cache",
        signal: controller.signal,
        headers: { "Cache-Control": "no-cache" },
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        try {
          const config = await response.json();
          if (config?.backend_port) {
            const url = `http://localhost:${config.backend_port}`;
            const isReachable = await checkUrlReachable(url, { timeout: 1500 });

            if (isReachable) {
              console.log(
                `✅ Backend confirmed running on port ${config.backend_port}`,
              );
              backendUrlCache.url = url;
              backendUrlCache.lastChecked = now;
              return url;
            }
          }
        } catch (e) {
          console.debug("Error parsing backend config:", e);
        }
      }
    } catch (error) {
      console.debug("Could not read backend config:", error);
    }

    // Fallback to common ports with optimized checking
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // Reduced timeout

    try {
      // Check ports sequentially instead of parallel to reduce load
      for (const port of DEFAULT_PORTS) {
        if (controller.signal.aborted) break;

        const isReachable = await checkUrlReachable(
          `http://localhost:${port}`,
          {
            signal: controller.signal,
            timeout: 800, // Faster individual checks
          },
        );

        if (isReachable) {
          const url = `http://localhost:${port}`;
          console.log(`✅ Found working backend on port ${port}`);
          backendUrlCache.url = url;
          backendUrlCache.lastChecked = now;
          clearTimeout(timeoutId);
          return url;
        }
      }
    } finally {
      clearTimeout(timeoutId);
      controller.abort();
    }
  } catch (error) {
    console.debug("Backend connection attempt failed:", error);
    const connectionError = new Error(
      "Could not connect to backend. Please make sure the backend server is running.",
    );
    backendUrlCache.lastError = connectionError;
    backendUrlCache.lastChecked = now;
    console.warn("Using fallback backend URL:", FALLBACK_URL);
    return FALLBACK_URL;
  } finally {
    checkInProgress = false;
    backendUrlCache.isChecking = false;
  }

  // If we get here, no backend was found but we didn't throw
  console.warn("No backend found, using fallback URL:", FALLBACK_URL);
  return FALLBACK_URL;
};

/**
 * Get cached backend URL without triggering new detection
 */
export const getCachedBackendUrl = (): string => {
  const now = Date.now();

  // Return cached URL if available and not too old
  if (
    backendUrlCache.url &&
    now - backendUrlCache.lastChecked < BACKEND_URL_CACHE_TTL
  ) {
    return backendUrlCache.url;
  }

  // Return fallback if no cache or cache is stale
  return FALLBACK_URL;
};

/**
 * Reset the backend URL cache to force re-detection
 */
export const resetBackendUrlCache = (): void => {
  backendUrlCache.url = null;
  backendUrlCache.lastChecked = 0;
  backendUrlCache.lastError = null;
  backendUrlCache.isChecking = false;
};

// Cache the backend URL to avoid repeated detection
let cachedBackendUrl: string | null = null;

export const getCachedBackendUrlAsync = async (): Promise<string> => {
  if (!cachedBackendUrl) {
    cachedBackendUrl = await getBackendUrl();
  }
  return cachedBackendUrl;
};
