import { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Activity, Server, Database, ShieldAlert, Zap, RefreshCw } from "lucide-react";
import { healthApi } from "../lib/api";

export function SystemStatus() {
    const [healthData, setHealthData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(new Date());

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

                {/* Experiment Controls */}
                <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <ShieldAlert className="h-5 w-5 text-red-500" />
                        Fault Injection (Chaos Mesh)
                    </h2>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Node Failure</div>
                            <p className="text-xs text-muted-foreground">Randomly kill one Gitea pod to test failover.</p>
                            <Button variant="destructive" size="sm" className="w-full" disabled>
                                Inject PodKill
                            </Button>
                            <p className="text-xs text-muted-foreground italic">Requires Kubernetes cluster</p>
                        </div>
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">Network Partition</div>
                            <p className="text-xs text-muted-foreground">Isolate CRDB Node-2 from the cluster.</p>
                            <Button variant="destructive" size="sm" className="w-full" disabled>
                                Inject Partition
                            </Button>
                            <p className="text-xs text-muted-foreground italic">Requires Kubernetes cluster</p>
                        </div>
                        <div className="p-4 border rounded-md bg-muted/20 space-y-3">
                            <div className="font-medium text-sm">High Latency</div>
                            <p className="text-xs text-muted-foreground">Add 500ms delay to all outgoing packets.</p>
                            <Button variant="outline" size="sm" className="w-full border-red-200 text-red-600 hover:bg-red-50" disabled>
                                Inject Latency
                            </Button>
                            <p className="text-xs text-muted-foreground italic">Requires Kubernetes cluster</p>
                        </div>
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

                    <div className="grid gap-6 md:grid-cols-2">
                        {/* Mock Graph 1 */}
                        <div className="border rounded-md p-4 h-64 flex flex-col items-center justify-center bg-muted/10 relative overflow-hidden">
                            <div className="absolute inset-0 flex items-center justify-center opacity-10">
                                {/* Just a visual noise pattern */}
                                <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                                    <path d="M0,50 Q25,30 50,50 T100,50" fill="none" stroke="currentColor" strokeWidth="2" />
                                </svg>
                            </div>
                            <span className="font-mono text-sm text-muted-foreground">Throughput (Req/sec)</span>
                            <div className="text-3xl font-bold mt-2">
                                {healthData?.status === "healthy" ? "1,245" : "0"}
                            </div>
                        </div>

                        {/* Mock Graph 2 */}
                        <div className="border rounded-md p-4 h-64 flex flex-col items-center justify-center bg-muted/10">
                            <span className="font-mono text-sm text-muted-foreground">Avg Recovery Time (Last 5 Runs)</span>
                            <div className="text-3xl font-bold mt-2 text-green-600">4.2s</div>
                            <p className="text-xs text-muted-foreground mt-2">Simulated data</p>
                        </div>
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
