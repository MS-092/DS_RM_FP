import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { ArrowLeft, GitBranch, Star, GitFork, AlertCircle, Folder, File, Download } from "lucide-react";
import { repositoriesApi } from "../lib/api";

export function RepositoryDetail() {
    const { owner, repo } = useParams();
    const fullName = `${owner}/${repo}`;

    const [repository, setRepository] = useState(null);
    const [contents, setContents] = useState([]);
    const [currentPath, setCurrentPath] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [fileContent, setFileContent] = useState(null);
    const [viewingFile, setViewingFile] = useState(false);

    useEffect(() => {
        fetchRepository();
        fetchContents("");
    }, [owner, repo]);

    const fetchRepository = async () => {
        try {
            const response = await repositoriesApi.getById(owner, repo);
            setRepository(response.data);
        } catch (err) {
            console.error("Error fetching repository:", err);
            setError("Failed to load repository details");
        }
    };

    const fetchContents = async (path) => {
        try {
            setLoading(true);
            setViewingFile(false);
            setFileContent(null);
            const response = await repositoriesApi.getContents(owner, repo, path);
            setContents(response.data);
            setCurrentPath(path);
            setError(null);
        } catch (err) {
            console.error("Error fetching contents:", err);
            setError("Failed to load repository contents");
        } finally {
            setLoading(false);
        }
    };

    const handleItemClick = async (item) => {
        if (item.type === "dir") {
            fetchContents(item.path);
        } else {
            // View file
            try {
                setLoading(true);
                const response = await repositoriesApi.getFile(owner, repo, item.path);
                setFileContent(response.data);
                setViewingFile(true);
                setCurrentPath(item.path);
            } catch (err) {
                console.error("Error fetching file:", err);
                setError("Failed to load file content");
            } finally {
                setLoading(false);
            }
        }
    };

    const navigateUp = () => {
        if (currentPath) {
            const parts = currentPath.split('/');
            parts.pop();
            const newPath = parts.join('/');
            fetchContents(newPath);
        }
    };

    const decodeBase64Content = (content, encoding) => {
        if (encoding === "base64") {
            try {
                return atob(content);
            } catch (e) {
                return content;
            }
        }
        return content;
    };

    if (!repository && !loading) {
        return (
            <div className="container py-10 max-w-screen-xl">
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                    {error || "Repository not found"}
                </div>
                <Link to="/repos" className="inline-flex items-center gap-2 mt-4 text-sm hover:underline">
                    <ArrowLeft className="h-4 w-4" />
                    Back to repositories
                </Link>
            </div>
        );
    }

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-6">
                {/* Breadcrumb */}
                <Link to="/repos" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground w-fit">
                    <ArrowLeft className="h-4 w-4" />
                    Back to repositories
                </Link>

                {/* Repository Header */}
                {repository && (
                    <div className="flex flex-col gap-4">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight">{repository.name}</h1>
                            <p className="text-muted-foreground mt-2">
                                {repository.description || "No description provided"}
                            </p>
                        </div>

                        {/* Stats */}
                        <div className="flex items-center gap-6 text-sm">
                            <div className="flex items-center gap-1">
                                <Star className="h-4 w-4" />
                                <span>{repository.stars_count} stars</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <GitFork className="h-4 w-4" />
                                <span>{repository.forks_count} forks</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <AlertCircle className="h-4 w-4" />
                                <span>{repository.open_issues_count} issues</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <GitBranch className="h-4 w-4" />
                                <span>{repository.default_branch}</span>
                            </div>
                        </div>

                        {/* Clone URLs */}
                        <div className="rounded-lg border bg-card p-4">
                            <h3 className="font-semibold mb-3">Clone Repository</h3>
                            <div className="space-y-2">
                                <div>
                                    <label className="text-sm text-muted-foreground">HTTPS</label>
                                    <div className="flex gap-2 mt-1">
                                        <code className="flex-1 px-3 py-2 bg-muted rounded text-sm">
                                            {repository.clone_url}
                                        </code>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => navigator.clipboard.writeText(repository.clone_url)}
                                        >
                                            Copy
                                        </Button>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm text-muted-foreground">SSH</label>
                                    <div className="flex gap-2 mt-1">
                                        <code className="flex-1 px-3 py-2 bg-muted rounded text-sm">
                                            {repository.ssh_url}
                                        </code>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => navigator.clipboard.writeText(repository.ssh_url)}
                                        >
                                            Copy
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* File Browser */}
                <div className="rounded-lg border bg-card">
                    <div className="p-4 border-b bg-muted/40">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <h3 className="font-semibold">Files</h3>
                                {currentPath && (
                                    <>
                                        <span className="text-muted-foreground">/</span>
                                        <span className="text-sm text-muted-foreground">{currentPath}</span>
                                    </>
                                )}
                            </div>
                            {currentPath && !viewingFile && (
                                <Button variant="outline" size="sm" onClick={navigateUp}>
                                    <ArrowLeft className="h-4 w-4 mr-2" />
                                    Up
                                </Button>
                            )}
                            {viewingFile && (
                                <Button variant="outline" size="sm" onClick={() => fetchContents(currentPath.split('/').slice(0, -1).join('/'))}>
                                    <ArrowLeft className="h-4 w-4 mr-2" />
                                    Back to files
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Loading */}
                    {loading && (
                        <div className="p-8 text-center text-muted-foreground">
                            Loading...
                        </div>
                    )}

                    {/* Error */}
                    {error && !loading && (
                        <div className="p-4 text-red-600">
                            {error}
                        </div>
                    )}

                    {/* File Content View */}
                    {viewingFile && fileContent && !loading && (
                        <div className="p-4">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <File className="h-4 w-4" />
                                    <span className="font-medium">{fileContent.name}</span>
                                    <span className="text-sm text-muted-foreground">
                                        ({fileContent.size} bytes)
                                    </span>
                                </div>
                                {fileContent.download_url && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => window.open(fileContent.download_url, '_blank')}
                                    >
                                        <Download className="h-4 w-4 mr-2" />
                                        Download
                                    </Button>
                                )}
                            </div>
                            <pre className="bg-muted p-4 rounded overflow-x-auto text-sm">
                                <code>{decodeBase64Content(fileContent.content, fileContent.encoding)}</code>
                            </pre>
                        </div>
                    )}

                    {/* Directory Listing */}
                    {!viewingFile && !loading && !error && contents.length > 0 && (
                        <div>
                            {contents.map((item, index) => (
                                <div
                                    key={index}
                                    className="p-4 border-b last:border-0 hover:bg-muted/30 cursor-pointer transition-colors"
                                    onClick={() => handleItemClick(item)}
                                >
                                    <div className="flex items-center gap-3">
                                        {item.type === "dir" ? (
                                            <Folder className="h-5 w-5 text-blue-500" />
                                        ) : (
                                            <File className="h-5 w-5 text-muted-foreground" />
                                        )}
                                        <span className="font-medium">{item.name}</span>
                                        {item.type === "file" && (
                                            <span className="text-sm text-muted-foreground ml-auto">
                                                {item.size} bytes
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Empty State */}
                    {!viewingFile && !loading && !error && contents.length === 0 && (
                        <div className="p-8 text-center text-muted-foreground">
                            This directory is empty
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
