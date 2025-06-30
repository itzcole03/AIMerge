import React, { useState, useEffect } from "react";
import { Play, Square, Settings, Bot, Brain, Zap, Monitor } from "lucide-react";

interface AutomationSettings {
  autonomousMode: boolean;
  acceptRate: number;
  supervisorRate: number;
  cycleTime: number;
  hotkeysEnabled: boolean;
}

interface AgentStatus {
  isActive: boolean;
  mode: "main" | "supervisor";
  lastAction: string;
  timestamp: Date;
}

export const CopilotIntegration: React.FC = () => {
  const [automationSettings, setAutomationSettings] =
    useState<AutomationSettings>({
      autonomousMode: false,
      acceptRate: 85,
      supervisorRate: 70,
      cycleTime: 180,
      hotkeysEnabled: true,
    });

  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    isActive: false,
    mode: "main",
    lastAction: "None",
    timestamp: new Date(),
  });

  const [isAutomationRunning, setIsAutomationRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev.slice(-50), `[${timestamp}] ${message}`]);
  };

  const toggleAutomation = async () => {
    try {
      if (isAutomationRunning) {
        await fetch("/api/automation/stop", { method: "POST" });
        setIsAutomationRunning(false);
        addLog("Automation stopped");
      } else {
        await fetch("/api/automation/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(automationSettings),
        });
        setIsAutomationRunning(true);
        addLog("Automation started");
      }
    } catch (error) {
      addLog(
        `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  };

  const manualAccept = async () => {
    try {
      await fetch("/api/automation/accept", { method: "POST" });
      addLog("Manual accept triggered");
      setAgentStatus((prev) => ({
        ...prev,
        lastAction: "Accept",
        timestamp: new Date(),
      }));
    } catch (error) {
      addLog(
        `Accept error: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  };

  const manualReject = async () => {
    try {
      await fetch("/api/automation/reject", { method: "POST" });
      addLog("Manual reject triggered");
      setAgentStatus((prev) => ({
        ...prev,
        lastAction: "Reject",
        timestamp: new Date(),
      }));
    } catch (error) {
      addLog(
        `Reject error: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  };

  const toggleAutonomousMode = () => {
    setAutomationSettings((prev) => ({
      ...prev,
      autonomousMode: !prev.autonomousMode,
    }));
    addLog(
      `Autonomous mode ${!automationSettings.autonomousMode ? "enabled" : "disabled"}`,
    );
  };

  const switchAgent = (mode: "main" | "supervisor") => {
    setAgentStatus((prev) => ({ ...prev, mode, timestamp: new Date() }));
    addLog(`Switched to ${mode} agent`);
  };

  useEffect(() => {
    // Initialize automation status
    fetch("/api/automation/status")
      .then((res) => res.json())
      .then((data) => {
        setIsAutomationRunning(data.isRunning);
        setAgentStatus(data.agentStatus);
      })
      .catch(() => addLog("Failed to fetch automation status"));

    // Set up keyboard shortcuts
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!automationSettings.hotkeysEnabled) return;

      switch (event.key) {
        case "F6":
          event.preventDefault();
          manualAccept();
          break;
        case "F7":
          event.preventDefault();
          manualReject();
          break;
        case "F8":
          event.preventDefault();
          toggleAutonomousMode();
          break;
        case "F9":
          event.preventDefault();
          toggleAutomation();
          break;
        case "F10":
          event.preventDefault();
          switchAgent("supervisor");
          break;
        case "F11":
          event.preventDefault();
          switchAgent("main");
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [automationSettings.hotkeysEnabled]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Bot className="w-8 h-8 text-blue-500" />
            AI Copilot Automation
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Intelligent automation for AI-powered development workflow
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${isAutomationRunning ? "bg-green-500" : "bg-gray-400"}`}
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isAutomationRunning ? "Running" : "Stopped"}
          </span>
        </div>
      </div>

      {/* Main Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Automation Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Automation Controls
          </h3>

          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                onClick={toggleAutomation}
                className={`flex-1 px-4 py-3 rounded-lg font-semibold text-white transition-colors ${
                  isAutomationRunning
                    ? "bg-red-500 hover:bg-red-600"
                    : "bg-green-500 hover:bg-green-600"
                }`}
              >
                {isAutomationRunning ? (
                  <>
                    <Square className="w-4 h-4 inline mr-2" />
                    Stop Automation
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 inline mr-2" />
                    Start Automation
                  </>
                )}
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={manualAccept}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium"
              >
                Accept (F6)
              </button>
              <button
                onClick={manualReject}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium"
              >
                Reject (F7)
              </button>
            </div>

            <button
              onClick={toggleAutonomousMode}
              className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
                automationSettings.autonomousMode
                  ? "bg-blue-500 hover:bg-blue-600 text-white"
                  : "bg-gray-200 hover:bg-gray-300 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300"
              }`}
            >
              <Brain className="w-4 h-4 inline mr-2" />
              Autonomous Mode (F8)
            </button>
          </div>
        </div>

        {/* Agent Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Monitor className="w-5 h-5 text-purple-500" />
            Agent Status
          </h3>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Current Agent:
              </span>
              <span
                className={`px-2 py-1 rounded text-sm font-medium ${
                  agentStatus.mode === "main"
                    ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                    : "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                }`}
              >
                {agentStatus.mode === "main"
                  ? "Main Agent"
                  : "Supervisor Agent"}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Last Action:
              </span>
              <span className="text-sm text-gray-900 dark:text-white">
                {agentStatus.lastAction}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Timestamp:
              </span>
              <span className="text-sm text-gray-900 dark:text-white">
                {agentStatus.timestamp.toLocaleTimeString()}
              </span>
            </div>

            <div className="flex gap-2 mt-4">
              <button
                onClick={() => switchAgent("main")}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  agentStatus.mode === "main"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
                }`}
              >
                Main (F11)
              </button>
              <button
                onClick={() => switchAgent("supervisor")}
                className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  agentStatus.mode === "supervisor"
                    ? "bg-purple-500 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
                }`}
              >
                Supervisor (F10)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-gray-500" />
          Automation Settings
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Main Agent Accept Rate: {automationSettings.acceptRate}%
            </label>
            <input
              type="range"
              min="50"
              max="95"
              value={automationSettings.acceptRate}
              onChange={(e) =>
                setAutomationSettings((prev) => ({
                  ...prev,
                  acceptRate: parseInt(e.target.value),
                }))
              }
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Supervisor Accept Rate: {automationSettings.supervisorRate}%
            </label>
            <input
              type="range"
              min="50"
              max="90"
              value={automationSettings.supervisorRate}
              onChange={(e) =>
                setAutomationSettings((prev) => ({
                  ...prev,
                  supervisorRate: parseInt(e.target.value),
                }))
              }
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Cycle Time: {automationSettings.cycleTime}s
            </label>
            <input
              type="range"
              min="60"
              max="600"
              value={automationSettings.cycleTime}
              onChange={(e) =>
                setAutomationSettings((prev) => ({
                  ...prev,
                  cycleTime: parseInt(e.target.value),
                }))
              }
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="hotkeys"
              checked={automationSettings.hotkeysEnabled}
              onChange={(e) =>
                setAutomationSettings((prev) => ({
                  ...prev,
                  hotkeysEnabled: e.target.checked,
                }))
              }
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <label
              htmlFor="hotkeys"
              className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Enable Hotkeys
            </label>
          </div>
        </div>
      </div>

      {/* Activity Log */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Activity Log</h3>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
          {logs.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400">
              No activity yet...
            </p>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className="text-gray-800 dark:text-gray-200 mb-1"
              >
                {log}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Hotkey Reference */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          Hotkey Reference
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm text-blue-800 dark:text-blue-200">
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F6</kbd>{" "}
            Manual Accept
          </div>
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F7</kbd>{" "}
            Manual Reject
          </div>
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F8</kbd>{" "}
            Toggle Autonomous
          </div>
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F9</kbd>{" "}
            Toggle Automation
          </div>
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F10</kbd>{" "}
            Supervisor Agent
          </div>
          <div>
            <kbd className="bg-blue-200 dark:bg-blue-800 px-1 rounded">F11</kbd>{" "}
            Main Agent
          </div>
        </div>
      </div>
    </div>
  );
};
