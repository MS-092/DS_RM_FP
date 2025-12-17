import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Search, MessageSquare, AlertCircle, CheckCircle2 } from "lucide-react";
import { issuesApi } from "../lib/api";

export function IssueList() {
    const [filter, setFilter] = useState("all");
    const [searchTerm, setSearchTerm] = useState("");
    const [issues, setIssues] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchIssues();
    }, []);

    const fetchIssues = async () => {
        try {
            setLoading(true);
            const response = await issuesApi.getAll();
            setIssues(response.data);
            setError(null);
        } catch (err) {
            setError("Failed to load issues. Please ensure the backend is running.");
            console.error("Error fetching issues:", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredIssues = issues.filter(issue => {
        const matchesFilter = filter === "all" || issue.status === filter;
        const matchesSearch =
            issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            issue.repository.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight">System Reliability Log</h1>
                    <p className="text-muted-foreground">Automated log of system failures, recovery events, and research anomalies detected during experiments.</p>
                </div>

                {/* Controls */}
                <div className="flex flex-col sm:flex-row items-center gap-4">
                    <div className="relative flex-1 w-full">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Filter issues..."
                            className="pl-8 bg-background"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2 w-full sm:w-auto">
                        <Button variant={filter === "all" ? "default" : "outline"} onClick={() => setFilter("all")}>All</Button>
                        <Button variant={filter === "open" ? "default" : "outline"} onClick={() => setFilter("open")}>Open</Button>
                        <Button variant={filter === "closed" ? "default" : "outline"} onClick={() => setFilter("closed")}>Closed</Button>
                    </div>
                    <Link to="/issues/new" className="w-full sm:w-auto">
                        <Button className="w-full">New Issue</Button>
                    </Link>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12 text-muted-foreground">
                        Loading issues...
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                        {error}
                    </div>
                )}

                {/* Empty State */}
                {!loading && !error && filteredIssues.length === 0 && (
                    <div className="text-center py-12 text-muted-foreground">
                        No issues found. {issues.length === 0 ? "Create your first issue!" : "Try adjusting your filters."}
                    </div>
                )}

                {/* List */}
                {!loading && !error && filteredIssues.length > 0 && (
                    <div className="rounded-md border bg-card text-card-foreground shadow-sm">
                        <div className="p-4 border-b bg-muted/40 font-medium grid grid-cols-12 gap-4 text-sm text-muted-foreground">
                            <div className="col-span-1 text-center">Status</div>
                            <div className="col-span-7">Title</div>
                            <div className="col-span-2">Repo</div>
                            <div className="col-span-2 text-right">Activity</div>
                        </div>

                        {filteredIssues.map((issue) => (
                            <div key={issue.id} className="p-4 border-b last:border-0 grid grid-cols-12 gap-4 items-center hover:bg-muted/30 transition-colors">
                                <div className="col-span-1 flex justify-center">
                                    {issue.status === "open" ? (
                                        <AlertCircle className="h-5 w-5 text-green-600" />
                                    ) : (
                                        <CheckCircle2 className="h-5 w-5 text-red-600" />
                                    )}
                                </div>
                                <div className="col-span-7 space-y-1">
                                    <Link to={`/issues/${issue.id}`} className="font-semibold hover:underline block truncate">
                                        {issue.title}
                                    </Link>
                                    <div className="text-xs text-muted-foreground">
                                        #{issue.id} opened {new Date(issue.created_at).toLocaleDateString()} by <span className="font-medium text-foreground">{issue.created_by}</span>
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 truncate max-w-full">
                                        {issue.repository}
                                    </span>
                                </div>
                                <div className="col-span-2 text-right flex items-center justify-end gap-1 text-muted-foreground text-sm">
                                    <MessageSquare className="h-4 w-4" />
                                    0
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
