import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { LandingPage } from "./pages/LandingPage";
import { RepositoryList } from "./pages/RepositoryList";
import { RepositoryDetail } from "./pages/RepositoryDetail";
import { IssueList } from "./pages/IssueList";
import { IssueDetail } from "./pages/IssueDetail";
import { SystemStatus } from "./pages/SystemStatus";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background font-sans antialiased text-foreground selection:bg-indigo-100 selection:text-indigo-900">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/repos" element={<RepositoryList />} />
            <Route path="/repos/:owner/:repo" element={<RepositoryDetail />} />
            <Route path="/issues" element={<IssueList />} />
            <Route path="/issues/:id" element={<IssueDetail />} />
            <Route path="/status" element={<SystemStatus />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
