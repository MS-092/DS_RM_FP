import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { ArrowLeft, GitBranch, Star, GitFork, AlertCircle, Folder, File, Download, Code, GitCommit } from "lucide-react";
import { repositoriesApi } from "../lib/api";

export function RepositoryDetail() {
    const { owner, repo } = useParams();
    const fullName = `${owner}/${repo}`;

    const [repository, setRepository] = useState(null);
    const [activeTab, setActiveTab] = useState("files"); // files, issues, branches

    // Data States
    const [contents, setContents] = useState([]);
    const [issues, setIssues] = useState([]);
    const [branches, setBranches] = useState([]);

    // File Browser States
    const [currentPath, setCurrentPath] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [fileContent, setFileContent] = useState(null);
    const [viewingFile, setViewingFile] = useState(false);

    useEffect(() => {
        fetchRepository();
        fetchContents("");
    }, [owner, repo]);

    // Fetch handlers
    const fetchRepository = async () => {
        try {
            setLoading(true);
            const response = await repositoriesApi.getById(owner, repo);
            setRepository(response.data);
            setError(null);
        } catch (err) {
            console.error("Error fetching repository:", err);
            setError("Failed to load repository details");
        } finally {
            setLoading(false);
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
            setError("Failed to load contents");
        } finally {
            setLoading(false);
        }
    };

    const fetchIssues = async () => {
        try {
            setLoading(true);
            const response = await repositoriesApi.getIssues(owner, repo);
            setIssues(response.data);
        } catch (err) {
            console.error("Error fetching issues:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchBranches = async () => {
        try {
            setLoading(true);
            const response = await repositoriesApi.getBranches(owner, repo);
            setBranches(response.data);
        } catch (err) {
            console.error("Error fetching branches:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === "files") fetchContents(currentPath || "");
        if (tab === "issues") fetchIssues();
        if (tab === "branches") fetchBranches();
    };

    const handleItemClick = async (item) => {
        if (item.type === "dir") {
            fetchContents(item.path);
        } else {
            try {
                setLoading(true);
                const response = await repositoriesApi.getFile(owner, repo, item.path);
                setFileContent(response.data);
                setViewingFile(true);
                setCurrentPath(item.path);
            } catch (err) {
                console.error("Error fetching file:", err);
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
            } catch (err) {
                return content;
            }
        }
        return content;
    };

    if (!repository && !loading && error) {
        return (
            <div className="container py-10 max-w-screen-xl">
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{error}</div>
                <Link to="/repos" className="inline-flex items-center gap-2 mt-4 text-sm hover:underline"><ArrowLeft className="h-4 w-4" />Back</Link>
            </div>
        );
    }

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-6">
                <Link to="/repos" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground w-fit">
                    <ArrowLeft className="h-4 w-4" /> Back to repositories
                </Link>

                {repository && (
                    <div className="flex flex-col gap-4">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight">{repository.name}</h1>
                            <p className="text-muted-foreground mt-2">{repository.description || "No description provided"}</p>
                        </div>
                        <div className="flex items-center gap-6 text-sm">
                            <div className="flex items-center gap-1"><Star className="h-4 w-4" /><span>{repository.stars_count} stars</span></div>
                            <div className="flex items-center gap-1"><GitFork className="h-4 w-4" /><span>{repository.forks_count} forks</span></div>
                            <div className="flex items-center gap-1"><AlertCircle className="h-4 w-4" /><span>{repository.open_issues_count} issues</span></div>
                        </div>
                    </div>
                )}

                {/* Tabs */}
                <div className="flex gap-2 border-b">
                    <Button variant={activeTab === 'files' ? 'default' : 'ghost'} onClick={() => handleTabChange('files')} size="sm" className="rounded-b-none rounded-t-lg">
                        <Code className="h-4 w-4 mr-2" /> Code
                    </Button>
                    <Button variant={activeTab === 'issues' ? 'default' : 'ghost'} onClick={() => handleTabChange('issues')} size="sm" className="rounded-b-none rounded-t-lg">
                        <AlertCircle className="h-4 w-4 mr-2" /> Issues
                    </Button>
                    <Button variant={activeTab === 'branches' ? 'default' : 'ghost'} onClick={() => handleTabChange('branches')} size="sm" className="rounded-b-none rounded-t-lg">
                        <GitBranch className="h-4 w-4 mr-2" /> Branches
                    </Button>
                </div>

                <div className="rounded-lg border bg-card min-h-[300px]">
                    {/* FILES TAB */}
                    {activeTab === 'files' && (
                        <div className="p-0">
                            <div className="p-4 border-b bg-muted/40 flex justify-between items-center">
                                <h3 className="font-semibold flex items-center gap-2">
                                    Files <span className="text-sm font-normal text-muted-foreground">{currentPath ? ` / ${currentPath}` : ' / root'}</span>
                                </h3>
                                {currentPath && !viewingFile && <Button variant="outline" size="sm" onClick={navigateUp}>Up</Button>}
                                {viewingFile && <Button variant="outline" size="sm" onClick={() => fetchContents(currentPath.split('/').slice(0, -1).join('/'))}>Back to files</Button>}
                            </div>

                            {viewingFile && fileContent ? (
                                <div className="p-4">
                                    <div className="flex justify-between mb-4">
                                        <span className="font-mono text-sm">{fileContent.name} ({fileContent.size} bytes)</span>
                                        {fileContent.download_url && <Button variant="outline" size="sm" onClick={() => window.open(fileContent.download_url)}>Download</Button>}
                                    </div>
                                    <pre className="bg-muted p-4 rounded overflow-auto text-sm"><code>{decodeBase64Content(fileContent.content, fileContent.encoding)}</code></pre>
                                </div>
                            ) : (
                                <div>
                                    {contents.map((item, i) => (
                                        <div key={i} className="p-4 border-b last:border-0 hover:bg-muted/30 cursor-pointer flex items-center gap-3" onClick={() => handleItemClick(item)}>
                                            {item.type === 'dir' ? <Folder className="h-5 w-5 text-blue-500" /> : <File className="h-5 w-5 text-muted-foreground" />}
                                            <span className="font-medium">{item.name}</span>
                                            {item.type === 'file' && <span className="ml-auto text-sm text-muted-foreground">{item.size} b</span>}
                                        </div>
                                    ))}
                                    {contents.length === 0 && !loading && <div className="p-8 text-center text-muted-foreground">Empty directory</div>}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ISSUES TAB */}
                    {activeTab === 'issues' && (
                        <div className="p-0">
                            {issues.map((issue) => (
                                <div key={issue.id} className="p-4 border-b last:border-0 hover:bg-muted/30 grid grid-cols-12 gap-4">
                                    <div className="col-span-1"><AlertCircle className="h-5 w-5 text-green-600" /></div>
                                    <div className="col-span-11">
                                        <div className="font-semibold">{issue.title}</div>
                                        <div className="text-xs text-muted-foreground">#{issue.number} opened by {issue.user?.username}</div>
                                    </div>
                                </div>
                            ))}
                            {issues.length === 0 && !loading && <div className="p-8 text-center text-muted-foreground">No open issues found in this repository.</div>}
                        </div>
                    )}

                    {/* BRANCHES TAB */}
                    {activeTab === 'branches' && (
                        <div className="p-0">
                            {branches.map((branch) => (
                                <div key={branch.name} className="p-4 border-b last:border-0 hover:bg-muted/30 flex items-center gap-3">
                                    <GitBranch className="h-5 w-5 text-purple-600" />
                                    <span className="font-semibold font-mono">{branch.name}</span>
                                    {branch.commit && <span className="text-xs text-muted-foreground ml-auto font-mono">{branch.commit.id.substring(0, 7)}</span>}
                                </div>
                            ))}
                            {branches.length === 0 && !loading && <div className="p-8 text-center text-muted-foreground">No branches found.</div>}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
