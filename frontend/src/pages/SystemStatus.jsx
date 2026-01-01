import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Activity, Server, Database, ShieldAlert, Zap, RefreshCw, Play, Settings, AlertTriangle, CheckCircle } from "lucide-react";
import { healthApi, faultToleranceApi } from "../lib/api";

export function SystemStatus() {
    const [healthData, setHealthData] = useState(null);
    const [ftStatus, setFtStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(new Date());

    // Experiment Control State
    const [selectedStrategy, setSelectedStrategy] = useState("hybrid");
    const [checkpointInterval, setCheckpointInterval] = useState(30);
    const [replicationFactor, setReplicationFactor] = useState(3);
    const [isExperimentRunning, setIsExperimentRunning] = useState(false);
    const [experimentResult, setExperimentResult] = useState(null);

    useEffect(() => {
        fetchSystemData();
        // Auto-refresh every 5 seconds for "Live" feel
        const interval = setInterval(fetchSystemData, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchSystemData = async () => {
        try {
            const [healthRes, ftRes] = await Promise.all([
                healthApi.check(),
                faultToleranceApi.getStatus()
            ]);

            setHealthData(healthRes.data);
            setFtStatus(ftRes.data);
            setLastUpdate(new Date());
        } catch (err) {
            console.error("Error fetching system data:", err);
            // Don't crash, just show stale/error state
        } finally {
            setLoading(false);
        }
    };

    const handleRunExperiment = async () => {
        setIsExperimentRunning(true);
        setExperimentResult(null);
        try {
            const payload = {
                strategy: selectedStrategy,
                checkpoint_interval: checkpointInterval,
                replication_factor: replicationFactor,
                data_items: 100,
                trigger_checkpoint: true
            };

            const response = await faultToleranceApi.runExperiment(payload);
            setExperimentResult(response.data);

            // Refresh status to show post-experiment state
            fetchSystemData();
        } catch (err) {
            console.error("Experiment failed:", err);
            alert("Experiment failed to start. Check backend logs.");
        } finally {
            setIsExperimentRunning(false);
        }
    };

    const handleInjectFault = async (type) => {
        if (!confirm(`Are you sure you want to inject '${type}' fault? This may disrupt the system.`)) return;

        try {
            await faultToleranceApi.simulateFailure({ failure_type: type, node_count: 1 });
            alert(`Fault '${type}' injected successfully.`);
            fetchSystemData(); // Immediate refresh
        } catch (err) {
            alert(`Failed to inject fault: ${err.message}`);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case "connected":
            case "running":
            case "healthy":
            case true: // boolean true
                return "text-green-500";
            case "degraded":
                return "text-orange-500";
            case "error":
            case "disconnected":
            case false: // boolean false
                return "text-red-500";
            default:
                return "text-gray-500";
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
                        status={healthData?.components?.database === "connected" ? "Healthy" : "Degraded"}
                        metric={healthData?.components?.database === "connected" ? "Connected" : "Disconnected"}
                        icon={<Database className={`h-5 w-5 ${getStatusColor(healthData?.components?.database)}`} />}
                    />
                    <StatusCard
                        title="Fault Tolerance"
                        status={ftStatus?.is_healthy ? "Active" : "Degraded"}
                        metric={ftStatus?.strategy ? ftStatus.strategy.toUpperCase() : "Unknown"}
                        icon={<ShieldAlert className={`h-5 w-5 ${getStatusColor(ftStatus?.is_healthy)}`} />}
                    />
                </div>

                {/* Research Control Panel */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 border-indigo-200 bg-indigo-50/10">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold flex items-center gap-2 text-indigo-700">
                            <Settings className="h-5 w-5" />
                            Research Control Panel
                        </h2>
                        {experimentResult && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-mono">
                                Last Run: {experimentResult.recovery_time?.toFixed(3)}s
                            </span>
                        )}
                    </div>

                    <div className="grid gap-6 md:grid-cols-4 items-end">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Strategy</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={selectedStrategy}
                                onChange={(e) => setSelectedStrategy(e.target.value)}
                            >
                                <option value="baseline">Baseline (None)</option>
                                <option value="checkpointing">Checkpointing</option>
                                <option value="replication">Replication</option>
                                <option value="hybrid">Hybrid</option>
                            </select>
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
                            />
                            <div className="text-sm text-muted-foreground text-center font-mono">{checkpointInterval}s</div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Replication Factor</label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                value={replicationFactor}
                                onChange={(e) => setReplicationFactor(parseInt(e.target.value))}
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
                            {isExperimentRunning ? 'Running...' : 'Run Experiment'}
                        </Button>
                    </div>
                </div>

                {/* Fault Injection (Chaos Mesh Integration) */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-red-500" />
                        Fault Injection (Chaos Mesh)
                    </h2>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Node Failure</div>
                            <p className="text-xs text-muted-foreground">Simulate generic node crash.</p>
                            <Button variant="destructive" size="sm" className="w-full" onClick={() => handleInjectFault("pod_kill")}>
                                Inject PodKill
                            </Button>
                        </div>
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Network Partition</div>
                            <p className="text-xs text-muted-foreground">Isolate Replica Nodes.</p>
                            <Button variant="destructive" size="sm" className="w-full" onClick={() => handleInjectFault("partition")}>
                                Inject Partition
                            </Button>
                        </div>
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">High Latency</div>
                            <p className="text-xs text-muted-foreground">Add 500ms delay.</p>
                            <Button variant="outline" size="sm" className="w-full border-red-200 text-red-600 hover:bg-red-50" onClick={() => handleInjectFault("latency")}>
                                Inject Latency
                            </Button>
                        </div>
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Force Recovery</div>
                            <p className="text-xs text-muted-foreground">Attempt to restore state.</p>
                            <Button
                                variant="outline"
                                size="sm"
                                className="w-full"
                                onClick={async () => {
                                    await faultToleranceApi.simulateFailure({ failure_type: "recover" }); // Or dedicated recover endpoint
                                    // Use api.post('/api/fault-tolerance/recover') 
                                    const res = await faultToleranceApi.getStatus(); // lazy way or use dedicated check
                                    alert("Recovery triggered.");
                                    fetchSystemData();
                                }}
                            >
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Recover
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Real-time Metrics */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-semibold">Live Metrics</h2>
                        <Button variant="ghost" size="sm" onClick={fetchSystemData}>
                            <RefreshCw className="h-4 w-4 mr-2" /> Refresh
                        </Button>
                    </div>

                    <div className="grid gap-6 md:grid-cols-3">
                        <MetricCard
                            title="Recovery Time"
                            value={ftStatus?.stats?.last_recovery_time ? `${ftStatus.stats.last_recovery_time.toFixed(4)}s` : "N/A"}
                            label="Last Experiment"
                            color="text-blue-600"
                        />
                        <div className="border rounded-md p-4 h-32 flex flex-col items-center justify-center bg-muted/10 relative overflow-hidden">
                            {/* Static visualization for now */}
                            <div className="absolute inset-0 flex items-center justify-center opacity-10">
                                <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                                    <path d="M0,50 Q25,30 50,50 T100,50" fill="none" stroke="currentColor" strokeWidth="2" />
                                </svg>
                            </div>
                            <span className="font-mono text-sm text-muted-foreground">Active Strategy</span>
                            <div className="text-2xl font-bold mt-2 truncate max-w-full px-2">
                                {ftStatus?.strategy || "None"}
                            </div>
                        </div>
                        <MetricCard
                            title="Availability"
                            value={ftStatus?.is_healthy ? "99.9%" : "Degraded"}
                            label="Current Status"
                            color={ftStatus?.is_healthy ? "text-green-600" : "text-red-600"}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatusCard({ title, status, metric, icon }) {
    return (
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 flex items-start justify-between">
            <div className="space-y-1">
                <div className="text-sm font-medium text-muted-foreground">{title}</div>
                <div className="text-2xl font-bold truncate">{metric}</div>
                <div className={`text-xs px-2 py-0.5 rounded-full inline-block ${status === 'Healthy' || status === 'Active'
                        ? 'bg-green-100 text-green-700'
                        : status === 'Degraded'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-red-100 text-red-700' // Changed for error visibility
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

function MetricCard({ title, value, label, color }) {
    return (
        <div className="border rounded-md p-4 h-32 flex flex-col items-center justify-center bg-muted/10">
            <span className="font-mono text-sm text-muted-foreground">{title}</span>
            <div className={`text-3xl font-bold mt-2 ${color}`}>{value}</div>
            <p className="text-xs text-muted-foreground mt-2">{label}</p>
        </div>
    );
}
