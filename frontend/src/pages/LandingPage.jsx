import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Server, ShieldCheck, GitBranch, Activity } from "lucide-react";

export function LandingPage() {
    return (
        <div className="flex flex-col min-h-[calc(100vh-3.5rem)]">
            {/* Hero Section */}
            <section className="flex-1 flex flex-col items-center justify-center space-y-10 py-24 text-center md:py-32 lg:py-40 overflow-hidden relative">
                <div className="absolute inset-0 -z-10 h-full w-full bg-white [background:radial-gradient(125%_125%_at_50%_10%,#fff_40%,#63e_100%)] opacity-20 dark:bg-black dark:[background:radial-gradient(125%_125%_at_50%_10%,#000_40%,#63e_100%)]"></div>

                <div className="container flex flex-col items-center gap-4 text-center relative z-10">
                    <div className="inline-flex items-center rounded-lg bg-muted px-3 py-1 text-sm font-medium">
                        <Activity className="mr-2 h-4 w-4 text-green-500" />
                        <span className="text-green-600 dark:text-green-400">System Nominal</span>
                        <span className="mx-2 h-4 w-[1px] bg-border"></span>
                        <span className="text-muted-foreground">Experiment Cycle v1.0</span>
                    </div>

                    <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400 pb-2">
                        Distributed Git Hosting <br className="hidden sm:inline" />
                        <span className="text-foreground">For High Availability</span>
                    </h1>

                    <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
                        Eliminate Single Points of Failure with our decentralized architecture.
                        Built on CockroachDB and Gitea for resilience and scalability experiments.
                    </p>

                    <div className="flex gap-4">
                        <Button size="lg" asChild className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20">
                            <Link to="/repos">
                                Explore Repositories <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                        <Button size="lg" variant="outline" asChild>
                            <Link to="/status">
                                View System Status
                            </Link>
                        </Button>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="container space-y-6 bg-slate-50 py-8 dark:bg-transparent md:py-12 lg:py-24 rounded-3xl mb-12 border border-slate-100 dark:border-slate-800">
                <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
                    <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl">
                        Research-Grade Reliability
                    </h2>
                    <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
                        Designed to test the limits of distributed systems recovery.
                    </p>
                </div>

                <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
                    <FeatureCard
                        icon={<ShieldCheck className="h-10 w-10 text-indigo-500" />}
                        title="Fault Tolerant"
                        description="Continues operation even if individual nodes fail. Configurable replication factors (2, 3, 5)."
                    />
                    <FeatureCard
                        icon={<Server className="h-10 w-10 text-purple-500" />}
                        title="Distributed Metadata"
                        description="Issue tracking data is sharded across CockroachDB nodes for strong consistency."
                    />
                    <FeatureCard
                        icon={<GitBranch className="h-10 w-10 text-pink-500" />}
                        title="Git Gateway"
                        description="Smart proxying of Git operations to backend Gitea clusters."
                    />
                </div>
            </section>
        </div>
    );
}

function FeatureCard({ icon, title, description }) {
    return (
        <div className="relative overflow-hidden rounded-lg border bg-background p-2">
            <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                {icon}
                <div className="space-y-2">
                    <h3 className="font-bold">{title}</h3>
                    <p className="text-sm text-muted-foreground">{description}</p>
                </div>
            </div>
        </div>
    )
}
