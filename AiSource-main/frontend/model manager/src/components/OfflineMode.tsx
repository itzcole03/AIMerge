import React from "react";
import { AlertTriangle, Wifi, WifiOff } from "lucide-react";

interface OfflineModeProps {
  onRetry?: () => void;
  isRetrying?: boolean;
}

export const OfflineMode: React.FC<OfflineModeProps> = ({
  onRetry,
  isRetrying,
}) => {
  return (
    <div className="max-w-2xl mx-auto mt-12 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 dark:bg-yellow-900/20 mb-4">
          <WifiOff className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
        </div>

        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Backend Offline
        </h3>

        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-sm mx-auto">
          The backend server is not running. The unified features (automation
          and agent orchestration) require the backend to be active.
        </p>

        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-left">
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                To enable full functionality:
              </h4>
              <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>1. Open a terminal in the project directory</li>
                <li>
                  2. Run the start script:{" "}
                  <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">
                    start.bat
                  </code>
                </li>
                <li>
                  3. Or start backend directly:{" "}
                  <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">
                    npm run start-backend
                  </code>
                </li>
                <li>4. Then refresh this page</li>
              </ol>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-center gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              disabled={isRetrying}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium transition-colors"
            >
              <Wifi
                className={`h-4 w-4 ${isRetrying ? "animate-pulse" : ""}`}
              />
              {isRetrying ? "Checking..." : "Check Backend"}
            </button>
          )}

          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            Refresh Page
          </button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
          AI model management features are still available in limited mode
        </p>
      </div>
    </div>
  );
};
