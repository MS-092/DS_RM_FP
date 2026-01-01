import { Link } from "react-router-dom";
import { Github, Activity, Layers, Server } from "lucide-react";
import { Button } from "./ui/button";

export function Navbar() {
    const username = localStorage.getItem('username');

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/login'; // Force refresh to clear state if needed
    };

    return (
        <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 max-w-screen-2xl items-center">
                <div className="mr-4 hidden md:flex">
                    <Link to="/" className="mr-6 flex items-center space-x-2">
                        <div className="h-6 w-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Github className="h-4 w-4 text-white" />
                        </div>
                        <span className="hidden font-bold sm:inline-block">
                            GitForge
                        </span>
                    </Link>
                    <nav className="flex items-center gap-6 text-sm">
                        <Link
                            to="/repos"
                            className="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center gap-2"
                        >
                            <Layers className="h-4 w-4" />
                            Repositories
                        </Link>
                        <Link
                            to="/issues"
                            className="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center gap-2"
                        >
                            <Activity className="h-4 w-4" />
                            Issues
                        </Link>
                        <Link
                            to="/status"
                            className="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center gap-2"
                        >
                            <Server className="h-4 w-4" />
                            System Status
                        </Link>
                    </nav>
                </div>
                <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                    <div className="w-full flex-1 md:w-auto md:flex-none"></div>
                    <nav className="flex items-center gap-2">
                        {username ? (
                            <>
                                <span className="text-sm text-slate-500 mr-2">Hi, {username}</span>
                                <Button variant="ghost" size="sm" onClick={handleLogout}>
                                    Logout
                                </Button>
                            </>
                        ) : (
                            <Button size="sm" asChild className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 border-0">
                                <a href="http://localhost:3000/user/login" target="_blank" rel="noreferrer">
                                    Access to Gitea
                                </a>
                            </Button>
                        )}
                    </nav>
                </div>
            </div>
        </nav>
    );
}
