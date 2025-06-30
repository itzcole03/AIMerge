import React, { useState, useEffect } from "react";
import {
  Users,
  Brain,
  Code,
  FileText,
  Bug,
  Cog,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
} from "lucide-react";

interface Agent {
  id: string;
  name: string;
  type: "architect" | "frontend" | "backend" | "qa" | "orchestrator";
  status: "idle" | "working" | "error" | "complete";
  currentTask?: string;
  progress?: number;
  lastUpdate: Date;
  capabilities: string[];
  model?: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo?: string;
  status: "pending" | "in-progress" | "completed" | "failed";
  priority: "low" | "medium" | "high" | "critical";
  createdAt: Date;
  estimatedTime?: number;
  dependencies?: string[];
}

export const AgentOrchestrator: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "architect",
      name: "Architect Agent",
      type: "architect",
      status: "idle",
      lastUpdate: new Date(),
      capabilities: [
        "System Design",
        "Architecture Planning",
        "Technology Selection",
      ],
      model: "llama3.1-70b",
    },
    {
      id: "frontend",
      name: "Frontend Agent",
      type: "frontend",
      status: "idle",
      lastUpdate: new Date(),
      capabilities: ["React Development", "UI/UX Design", "Component Creation"],
      model: "codellama-34b",
    },
    {
      id: "backend",
      name: "Backend Agent",
      type: "backend",
      status: "idle",
      lastUpdate: new Date(),
      capabilities: [
        "API Development",
        "Database Design",
        "Server Architecture",
      ],
      model: "codellama-34b",
    },
    {
      id: "qa",
      name: "QA Agent",
      type: "qa",
      status: "idle",
      lastUpdate: new Date(),
      capabilities: ["Test Creation", "Code Review", "Quality Assurance"],
      model: "llama3.1-8b",
    },
    {
      id: "orchestrator",
      name: "Orchestrator Agent",
      type: "orchestrator",
      status: "idle",
      lastUpdate: new Date(),
      capabilities: ["Task Coordination", "Resource Management", "Planning"],
      model: "llama3.1-70b",
    },
  ]);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [selectedPriority, setSelectedPriority] =
    useState<Task["priority"]>("medium");
  const [isCreatingTask, setIsCreatingTask] = useState(false);

  const getAgentIcon = (type: Agent["type"]) => {
    switch (type) {
      case "architect":
        return <Cog className="w-5 h-5" />;
      case "frontend":
        return <Code className="w-5 h-5" />;
      case "backend":
        return <Brain className="w-5 h-5" />;
      case "qa":
        return <Bug className="w-5 h-5" />;
      case "orchestrator":
        return <Users className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "idle":
        return <Clock className="w-4 h-4 text-gray-400" />;
      case "working":
        return <Activity className="w-4 h-4 text-blue-500 animate-pulse" />;
      case "complete":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: Agent["status"]) => {
    switch (status) {
      case "idle":
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
      case "working":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "complete":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    }
  };

  const getPriorityColor = (priority: Task["priority"]) => {
    switch (priority) {
      case "low":
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "high":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
      case "critical":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    }
  };

  const createTask = async () => {
    if (!newTaskTitle.trim() || !newTaskDescription.trim()) return;

    setIsCreatingTask(true);
    try {
      const newTask: Task = {
        id: Date.now().toString(),
        title: newTaskTitle,
        description: newTaskDescription,
        status: "pending",
        priority: selectedPriority,
        createdAt: new Date(),
      };

      // Send to backend for agent assignment
      await fetch("/api/agents/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });

      setTasks((prev) => [...prev, newTask]);
      setNewTaskTitle("");
      setNewTaskDescription("");
      setSelectedPriority("medium");
    } catch (error) {
      console.error("Failed to create task:", error);
    } finally {
      setIsCreatingTask(false);
    }
  };

  const assignTask = async (taskId: string, agentId: string) => {
    try {
      await fetch(`/api/agents/${agentId}/assign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId }),
      });

      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId
            ? { ...task, assignedTo: agentId, status: "in-progress" }
            : task,
        ),
      );

      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === agentId
            ? {
                ...agent,
                status: "working",
                currentTask: tasks.find((t) => t.id === taskId)?.title,
              }
            : agent,
        ),
      );
    } catch (error) {
      console.error("Failed to assign task:", error);
    }
  };

  useEffect(() => {
    // Fetch initial data
    const fetchData = async () => {
      try {
        const [agentsRes, tasksRes] = await Promise.all([
          fetch("/api/agents"),
          fetch("/api/agents/tasks"),
        ]);

        if (agentsRes.ok) {
          const agentsData = await agentsRes.json();
          setAgents(agentsData);
        }

        if (tasksRes.ok) {
          const tasksData = await tasksRes.json();
          setTasks(tasksData);
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    };

    fetchData();

    // Set up real-time updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const activeAgents = agents.filter(
    (agent) => agent.status === "working",
  ).length;
  const completedTasks = tasks.filter(
    (task) => task.status === "completed",
  ).length;
  const pendingTasks = tasks.filter((task) => task.status === "pending").length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Users className="w-8 h-8 text-purple-500" />
            Multi-Agent Orchestrator
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Coordinate and manage AI agents for complex development tasks
          </p>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
            <span>{activeAgents} Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>{completedTasks} Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full" />
            <span>{pendingTasks} Pending</span>
          </div>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  {getAgentIcon(agent.type)}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {agent.name}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {agent.model}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {getStatusIcon(agent.status)}
              </div>
            </div>

            <div className="mb-3">
              <span
                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}
              >
                {agent.status}
              </span>
            </div>

            {agent.currentTask && (
              <div className="mb-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Current Task:
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {agent.currentTask}
                </p>
                {agent.progress && (
                  <div className="mt-2">
                    <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${agent.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="space-y-1">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Capabilities:
              </p>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.slice(0, 2).map((capability, index) => (
                  <span
                    key={index}
                    className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded"
                  >
                    {capability}
                  </span>
                ))}
                {agent.capabilities.length > 2 && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    +{agent.capabilities.length - 2} more
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Task Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Create New Task */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-green-500" />
            Create New Task
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Task Title
              </label>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Enter task title..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Describe the task..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Priority
              </label>
              <select
                value={selectedPriority}
                onChange={(e) =>
                  setSelectedPriority(e.target.value as Task["priority"])
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <button
              onClick={createTask}
              disabled={
                isCreatingTask ||
                !newTaskTitle.trim() ||
                !newTaskDescription.trim()
              }
              className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isCreatingTask ? "Creating..." : "Create Task"}
            </button>
          </div>
        </div>

        {/* Task Queue */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Task Queue</h3>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {tasks.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No tasks yet. Create your first task to get started.
              </p>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {task.title}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {task.description}
                      </p>
                    </div>
                    <span
                      className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}
                    >
                      {task.priority}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        task.status === "pending"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                          : task.status === "in-progress"
                            ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                            : task.status === "completed"
                              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                              : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                      }`}
                    >
                      {task.status}
                    </span>

                    {task.status === "pending" && (
                      <select
                        onChange={(e) => assignTask(task.id, e.target.value)}
                        className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 dark:bg-gray-700 dark:text-white"
                        defaultValue=""
                      >
                        <option value="" disabled>
                          Assign to...
                        </option>
                        {agents
                          .filter((agent) => agent.status === "idle")
                          .map((agent) => (
                            <option key={agent.id} value={agent.id}>
                              {agent.name}
                            </option>
                          ))}
                      </select>
                    )}

                    {task.assignedTo && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Assigned to{" "}
                        {agents.find((a) => a.id === task.assignedTo)?.name}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
