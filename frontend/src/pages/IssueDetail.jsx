import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ArrowLeft, MessageSquare, Tag, User } from "lucide-react";
import { issuesApi, commentsApi } from "../lib/api";

export function IssueDetail() {
    const { id } = useParams();
    const [issue, setIssue] = useState(null);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchIssueData();
    }, [id]);

    const fetchIssueData = async () => {
        try {
            setLoading(true);
            const [issueResponse, commentsResponse] = await Promise.all([
                issuesApi.getById(id),
                commentsApi.getByIssueId(id)
            ]);
            setIssue(issueResponse.data);
            setComments(commentsResponse.data);
            setError(null);
        } catch (err) {
            setError("Failed to load issue details. Please ensure the backend is running.");
            console.error("Error fetching issue:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddComment = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        try {
            setSubmitting(true);
            const response = await commentsApi.create({
                issue_id: parseInt(id),
                user: "current-user", // TODO: Replace with actual user from auth
                body: newComment
            });
            setComments([...comments, response.data]);
            setNewComment("");
        } catch (err) {
            console.error("Error adding comment:", err);
            alert("Failed to add comment. Please try again.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="container py-10 max-w-screen-xl">
                <div className="text-center py-12 text-muted-foreground">
                    Loading issue...
                </div>
            </div>
        );
    }

    if (error || !issue) {
        return (
            <div className="container py-10 max-w-screen-xl">
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                    {error || "Issue not found"}
                </div>
                <Link to="/issues" className="inline-flex items-center gap-2 mt-4 text-sm hover:underline">
                    <ArrowLeft className="h-4 w-4" />
                    Back to issues
                </Link>
            </div>
        );
    }

    return (
        <div className="container py-10 max-w-screen-xl">
            <div className="flex flex-col gap-6">
                {/* Breadcrumb */}
                <Link to="/issues" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground w-fit">
                    <ArrowLeft className="h-4 w-4" />
                    Back to issues
                </Link>

                {/* Issue Header */}
                <div className="flex flex-col gap-4">
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                            <h1 className="text-3xl font-bold tracking-tight mb-2">{issue.title}</h1>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${issue.status === 'open'
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-gray-100 text-gray-800'
                                    }`}>
                                    {issue.status}
                                </span>
                                <span>#{issue.id}</span>
                                <span>opened {new Date(issue.created_at).toLocaleDateString()}</span>
                                <span>by {issue.created_by}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-3">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Description */}
                        <div className="rounded-lg border bg-card p-6">
                            <h2 className="font-semibold mb-3">Description</h2>
                            <p className="text-muted-foreground whitespace-pre-wrap">
                                {issue.description || "No description provided."}
                            </p>
                        </div>

                        {/* Comments */}
                        <div className="rounded-lg border bg-card p-6">
                            <h2 className="font-semibold mb-4 flex items-center gap-2">
                                <MessageSquare className="h-5 w-5" />
                                Comments ({comments.length})
                            </h2>

                            <div className="space-y-4">
                                {comments.map((comment) => (
                                    <div key={comment.id} className="border-l-2 border-muted pl-4 py-2">
                                        <div className="flex items-center gap-2 text-sm mb-2">
                                            <span className="font-medium">{comment.user}</span>
                                            <span className="text-muted-foreground">
                                                {new Date(comment.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                                            {comment.body}
                                        </p>
                                    </div>
                                ))}

                                {comments.length === 0 && (
                                    <p className="text-sm text-muted-foreground text-center py-4">
                                        No comments yet. Be the first to comment!
                                    </p>
                                )}
                            </div>

                            {/* Add Comment Form */}
                            <form onSubmit={handleAddComment} className="mt-6 space-y-3">
                                <textarea
                                    className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                    placeholder="Add a comment..."
                                    value={newComment}
                                    onChange={(e) => setNewComment(e.target.value)}
                                    disabled={submitting}
                                />
                                <Button type="submit" disabled={submitting || !newComment.trim()}>
                                    {submitting ? "Adding..." : "Add Comment"}
                                </Button>
                            </form>
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-4">
                        <div className="rounded-lg border bg-card p-4">
                            <h3 className="font-semibold mb-3 text-sm">Repository</h3>
                            <Link
                                to={`/repos/${issue.repository}`}
                                className="text-sm text-blue-600 hover:underline"
                            >
                                {issue.repository}
                            </Link>
                        </div>

                        <div className="rounded-lg border bg-card p-4">
                            <h3 className="font-semibold mb-3 text-sm flex items-center gap-2">
                                <User className="h-4 w-4" />
                                Author
                            </h3>
                            <p className="text-sm">{issue.created_by}</p>
                        </div>

                        <div className="rounded-lg border bg-card p-4">
                            <h3 className="font-semibold mb-3 text-sm">Created</h3>
                            <p className="text-sm text-muted-foreground">
                                {new Date(issue.created_at).toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
