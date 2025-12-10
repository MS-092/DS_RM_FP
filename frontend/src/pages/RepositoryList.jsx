import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Search, GitBranch, Star, GitFork, AlertCircle } from "lucide-react";
import { repositoriesApi } from "../lib/api";

export function RepositoryList() {
    const [repositories, setRepositories] = useState([]);
    const [filteredRepos, setFilteredRepos] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchRepositories();
    }, []);

    useEffect(() => {
        // Filter repositories based on search term
        if (searchTerm) {
            const filtered = repositories.filter(repo =>
                repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                repo.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                repo.full_name.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredRepos(filtered);
        } else {
            setFilteredRepos(repositories);
        }
    }, [searchTerm, repositories]);

    const fetchRepositories = async () => {
        try {
            setLoading(true);
            const response = await repositoriesApi.getAll();
            setRepositories(response.data);
            setFilteredRepos(response.data);
            setError(null);
        } catch (err) {
            console.error("Error fetching repositories:", err);
            setError("Failed to load repositories. Make sure Gitea is running and accessible.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-6">
                {/* Header */}
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight">Repositories</h1>
                    <p className="text-muted-foreground">
                        Browse and explore Git repositories hosted on Gitea
                    </p>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search repositories..."
                        className="pl-10"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12 text-muted-foreground">
                        Loading repositories...
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                        <div className="flex items-center gap-2">
                            <AlertCircle className="h-5 w-5" />
                            <div>
                                <p className="font-medium">Error loading repositories</p>
                                <p className="text-sm mt-1">{error}</p>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="mt-2"
                                    onClick={fetchRepositories}
                                >
                                    Retry
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Empty State */}
                {!loading && !error && filteredRepos.length === 0 && (
                    <div className="text-center py-12 text-muted-foreground">
                        {repositories.length === 0 ? (
                            <>
                                <p>No repositories found in Gitea.</p>
                                <p className="text-sm mt-2">Create a repository in Gitea to see it here.</p>
                            </>
                        ) : (
                            <p>No repositories match your search.</p>
                        )}
                    </div>
                )}

                {/* Repository Grid */}
                {!loading && !error && filteredRepos.length > 0 && (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {filteredRepos.map((repo) => (
                            <Link
                                key={repo.id}
                                to={`/repos/${repo.full_name}`}
                                className="block"
                            >
                                <div className="rounded-lg border bg-card p-6 hover:bg-accent transition-colors h-full">
                                    <div className="flex flex-col gap-3 h-full">
                                        {/* Repo Name */}
                                        <div className="flex items-start justify-between gap-2">
                                            <h3 className="font-semibold text-lg truncate flex-1">
                                                {repo.name}
                                            </h3>
                                            {repo.private && (
                                                <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
                                                    Private
                                                </span>
                                            )}
                                        </div>

                                        {/* Description */}
                                        <p className="text-sm text-muted-foreground line-clamp-2 flex-1">
                                            {repo.description || "No description provided"}
                                        </p>

                                        {/* Stats */}
                                        <div className="flex items-center gap-4 text-sm text-muted-foreground pt-2 border-t">
                                            <div className="flex items-center gap-1">
                                                <Star className="h-4 w-4" />
                                                <span>{repo.stars_count}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <GitFork className="h-4 w-4" />
                                                <span>{repo.forks_count}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <AlertCircle className="h-4 w-4" />
                                                <span>{repo.open_issues_count}</span>
                                            </div>
                                        </div>

                                        {/* Branch */}
                                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                            <GitBranch className="h-3 w-3" />
                                            <span>{repo.default_branch}</span>
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}

                {/* Results Count */}
                {!loading && !error && filteredRepos.length > 0 && (
                    <div className="text-sm text-muted-foreground text-center">
                        Showing {filteredRepos.length} of {repositories.length} repositories
                    </div>
                )}
            </div>
        </div>
    );
}
