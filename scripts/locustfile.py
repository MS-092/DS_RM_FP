"""
Locust Load Testing File for GitForge
Run with: locust -f scripts/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, events
import random

class GitForgeUser(HttpUser):
    """
    Simulates a user interacting with GitForge
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.issue_ids = []
        self.repo_names = []
    
    @task(5)
    def list_issues(self):
        """List all issues (most common operation)"""
        self.client.get("/api/issues")
    
    @task(3)
    def view_issue(self):
        """View a specific issue"""
        if self.issue_ids:
            issue_id = random.choice(self.issue_ids)
            self.client.get(f"/api/issues/{issue_id}")
        else:
            # If no issues cached, list them first
            response = self.client.get("/api/issues")
            if response.status_code == 200:
                issues = response.json()
                if issues:
                    self.issue_ids = [issue["id"] for issue in issues]
    
    @task(2)
    def create_issue(self):
        """Create a new issue"""
        issue_data = {
            "title": f"Load Test Issue {random.randint(1000, 9999)}",
            "description": "This is a load test issue",
            "repository": f"test-repo-{random.randint(1, 5)}",
            "created_by": f"user-{random.randint(1, 10)}"
        }
        
        response = self.client.post("/api/issues", json=issue_data)
        if response.status_code == 200:
            issue_id = response.json().get("id")
            if issue_id:
                self.issue_ids.append(issue_id)
    
    @task(2)
    def add_comment(self):
        """Add a comment to an issue"""
        if self.issue_ids:
            issue_id = random.choice(self.issue_ids)
            comment_data = {
                "issue_id": issue_id,
                "user": f"user-{random.randint(1, 10)}",
                "body": f"Load test comment {random.randint(1000, 9999)}"
            }
            self.client.post("/api/comments", json=comment_data)
    
    @task(1)
    def get_comments(self):
        """Get comments for an issue"""
        if self.issue_ids:
            issue_id = random.choice(self.issue_ids)
            self.client.get(f"/api/comments/issue/{issue_id}")
    
    @task(4)
    def list_repositories(self):
        """List repositories"""
        response = self.client.get("/api/repositories")
        if response.status_code == 200:
            repos = response.json()
            if repos:
                self.repo_names = [repo["full_name"] for repo in repos]
    
    @task(2)
    def view_repository(self):
        """View a specific repository"""
        if self.repo_names:
            repo_name = random.choice(self.repo_names)
            parts = repo_name.split('/')
            if len(parts) == 2:
                owner, repo = parts
                self.client.get(f"/api/repositories/{owner}/{repo}")
    
    @task(1)
    def browse_repository_contents(self):
        """Browse repository contents"""
        if self.repo_names:
            repo_name = random.choice(self.repo_names)
            parts = repo_name.split('/')
            if len(parts) == 2:
                owner, repo = parts
                self.client.get(f"/api/repositories/{owner}/{repo}/contents/")
    
    @task(3)
    def health_check(self):
        """Check system health"""
        self.client.get("/api/health")


class AdminUser(HttpUser):
    """
    Simulates an admin user performing administrative tasks
    """
    wait_time = between(2, 5)
    
    @task(1)
    def health_check(self):
        """Check system health"""
        self.client.get("/api/health")
    
    @task(1)
    def check_metrics(self):
        """Check Prometheus metrics"""
        self.client.get("/metrics")
    
    @task(2)
    def list_all_issues(self):
        """List all issues"""
        self.client.get("/api/issues")
    
    @task(1)
    def list_all_repositories(self):
        """List all repositories"""
        self.client.get("/api/repositories")


# Event listeners for custom statistics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("=" * 60)
    print("GitForge Load Test Starting")
    print(f"Target: {environment.host}")
    print("=" * 60)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("=" * 60)
    print("GitForge Load Test Complete")
    print("=" * 60)
