import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Activity, Server, Database, ShieldAlert, Zap, RefreshCw, Play, Settings } from "lucide-react";
import { healthApi } from "../lib/api";

const [faultToleranceMode, setFaultToleranceMode] = useState("none");

export function SystemStatus() {
    const [healthData, setHealthData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(new Date());

    // Experiment Control State
    const [checkpointInterval, setCheckpointInterval] = useState(30);
    const [replicationFactor, setReplicationFactor] = useState(3);
    const [isExperimentRunning, setIsExperimentRunning] = useState(false);

    useEffect(() => {
        fetchHealthData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchHealthData, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchHealthData = async () => {
        try {
            const response = await healthApi.check();
            setHealthData(response.data);
            setLastUpdate(new Date());
        } catch (err) {
            console.error("Error fetching health data:", err);
            setHealthData({
                status: "error",
                services: {
                    database: "disconnected",
                    api: "error"
                }
            });
        } finally {
            setLoading(false);
        }
    };

    const getServiceStatus = (service) => {
        if (!healthData) return "unknown";
        return healthData.services[service] || "unknown";
    };

    const getStatusColor = (status) => {
        switch (status) {
            case "connected":
            case "running":
            case "healthy":
                return "text-green-500";
            case "degraded":
                return "text-orange-500";
            case "error":
            case "disconnected":
                return "text-red-500";
            default:
                return "text-gray-500";
        }
    };

    const handleRunExperiment = async () => {
        console.log("Running experiment with:", {
            faultToleranceMode,
            checkpointInterval,
            replicationFactor
        });

        setIsExperimentRunning(true);

        try {
            // Determine which endpoint to call
            let endpoint = "";
            switch (faultToleranceMode) {
                case "checkpointing":
                    endpoint = "/checkpoint/update";
                    break;
                case "replication":
                    endpoint = "/replication/update";
                    break;
                case "combined":
                    endpoint = "/combined/update";
                    break;
                case "none":
                default:
                    console.log("No fault tolerance selected, skipping API call.");
                    setIsExperimentRunning(false);
                    return;
            }

            // Call the backend
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    checkpointInterval,
                    replicationFactor
                })
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            console.log("Experiment applied:", data);
            // Optionally update experiment results in UI
            // setExperimentResult(data);

        } catch (err) {
            console.error("Failed to run experiment:", err);
        } finally {
            setIsExperimentRunning(false);
        }
    };

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-8">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                        <Activity className="h-8 w-8 text-indigo-500" />
                        Research Dashboard
                    </h1>
                    <p className="text-muted-foreground">Monitor system health, active nodes, and inject faults for experiments.</p>
                    <p className="text-xs text-muted-foreground">
                        Last updated: {lastUpdate.toLocaleTimeString()}
                    </p>
                </div>

                {/* Cluster Status */}
                <div className="grid gap-6 md:grid-cols-3">
                    <StatusCard
                        title="Backend API"
                        status={healthData?.status === "healthy" ? "Healthy" : "Error"}
                        metric={healthData?.status === "healthy" ? "Online" : "Offline"}
                        icon={<Zap className={`h-5 w-5 ${getStatusColor(healthData?.status)}`} />}
                    />
                    <StatusCard
                        title="CockroachDB"
                        status={getServiceStatus("database") === "connected" ? "Healthy" : "Degraded"}
                        metric={getServiceStatus("database") === "connected" ? "Connected" : "Disconnected"}
                        icon={<Database className={`h-5 w-5 ${getStatusColor(getServiceStatus("database"))}`} />}
                    />
                    <StatusCard
                        title="Gitea Cluster"
                        status="Unknown"
                        metric="Not monitored"
                        icon={<Server className="h-5 w-5 text-gray-500" />}
                    />
                </div>

                {/* Research Control Panel (New) */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 border-indigo-200 bg-indigo-50/10">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-indigo-700">
                        <Settings className="h-5 w-5" />
                        Research Control Panel
                    </h2>
                    <div className="grid gap-6 md:grid-cols-3 items-end">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">
                                Fault Tolerance Technique
                            </label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm
                                        ring-offset-background focus-visible:outline-none focus-visible:ring-2
                                        focus-visible:ring-ring focus-visible:ring-offset-2"
                                value={faultToleranceMode}
                                onChange={(e) => setFaultToleranceMode(e.target.value)}
                            >
                                <option value="none">No Fault Tolerance</option>
                                <option value="checkpointing">Checkpointing Only</option>
                                <option value="replication">Replication Only</option>
                                <option value="combined">Checkpointing + Replication</option>
                            </select>
                            <p className="text-xs text-muted-foreground">
                                Select the fault tolerance strategy before launching the experiment.
                            </p>
                        </div>

                        <div className="text-xs font-mono text-indigo-600">
                            Active Mode: {faultToleranceMode.toUpperCase()}
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Checkpoint Interval</label>
                            <input
                                type="range"
                                min="15"
                                max="120"
                                step="15"
                                value={checkpointInterval}
                                onChange={(e) => setCheckpointInterval(parseInt(e.target.value))}
                                className="w-full"
                                disabled={faultToleranceMode === "replication" || faultToleranceMode === "none"}
                            />
                            <div className="text-sm text-muted-foreground text-center font-mono">{checkpointInterval}s</div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Replication Factor</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={replicationFactor}
                                onChange={(e) => setReplicationFactor(parseInt(e.target.value))}
                                disabled={faultToleranceMode === "checkpointing" || faultToleranceMode === "none"}
                            >
                                <option value="2">2 Nodes</option>
                                <option value="3">3 Nodes</option>
                                <option value="5">5 Nodes</option>
                            </select>
                        </div>
                        <Button
                            className="w-full bg-indigo-600 hover:bg-indigo-700"
                            onClick={handleRunExperiment}
                            disabled={isExperimentRunning}
                        >
                            <Play className={`h-4 w-4 mr-2 ${isExperimentRunning ? 'animate-spin' : ''}`} />
                            {isExperimentRunning ? 'Running Experiment...' : 'Trigger Experiment'}
                        </Button>
                    </div>
                </div>

                {/* Fault Injection (Original) */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <ShieldAlert className="h-5 w-5 text-red-500" />
                        Fault Injection (Chaos Mesh)
                    </h2>
                    <Button
                        variant="destructive"
                        size="sm"
                        className="w-full"
                        onClick={async () => {
                            setIsExperimentRunning(true);
                            try {
                                const response = await fetch("http://localhost:8000/api/run-fault-injection", {
                                    method: "POST"
                                });
                                const data = await response.json();
                                console.log(data);
                                alert(data.message); // Notify the user
                            } catch (err) {
                                console.error("Failed to start fault injection:", err);
                                alert("Failed to start fault injection");
                            } finally {
                                setIsExperimentRunning(false);
                            }
                        }}
                    >
                        Inject Failures
                    </Button>

                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Refresh Status</div>
                            <p className="text-xs text-muted-foreground">Manually refresh health status.</p>
                            <Button
                                variant="outline"
                                size="sm"
                                className="w-full"
                                onClick={fetchHealthData}
                                disabled={loading}
                            >
                                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                                {loading ? 'Refreshing...' : 'Refresh'}
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Real-time Metrics (Mock Grafana) */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-semibold">Live Metrics</h2>
                        <Button variant="ghost" size="sm" onClick={fetchHealthData}>
                            <RefreshCw className="h-4 w-4 mr-2" /> Refresh
                        </Button>
                    </div>

                    <div className="grid gap-6 md:grid-cols-3">
                        <div className="border rounded-md p-4 h-32 flex flex-col items-center justify-center bg-muted/10">
                            <span className="font-mono text-sm text-muted-foreground">Recovery Timer</span>
                            <div className="text-3xl font-bold mt-2 text-blue-600">4.2s</div>
                            <p className="text-xs text-muted-foreground mt-2">Last Run</p>
                        </div>
                        <div className="border rounded-md p-4 h-32 flex flex-col items-center justify-center bg-muted/10 relative overflow-hidden">
                            <div className="absolute inset-0 flex items-center justify-center opacity-10">
                                <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                                    <path d="M0,50 Q25,30 50,50 T100,50" fill="none" stroke="currentColor" strokeWidth="2" />
                                </svg>
                            </div>
                            <span className="font-mono text-sm text-muted-foreground">Throughput (Job/min)</span>
                            <div className="text-3xl font-bold mt-2">1,245</div>
                        </div>
                        <div className="border rounded-md p-4 h-32 flex flex-col items-center justify-center bg-muted/10">
                            <span className="font-mono text-sm text-muted-foreground">Availability</span>
                            <div className="text-3xl font-bold mt-2 text-green-600">99.9%</div>
                        </div>
                    </div>
                </div>
            </div>
    )
}

function StatusCard({ title, status, metric, icon }) {
    return (
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 flex items-start justify-between">
            <div className="space-y-1">
                <div className="text-sm font-medium text-muted-foreground">{title}</div>
                <div className="text-2xl font-bold">{metric}</div>
                <div className={`text-xs px-2 py-0.5 rounded-full inline-block ${status === 'Healthy'
                    ? 'bg-green-100 text-green-700'
                    : status === 'Degraded'
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                    {status}
                </div>
            </div>
            <div className="p-2 bg-muted/50 rounded-md">
                {icon}
            </div>
        </div>
    )
}
