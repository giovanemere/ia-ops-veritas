import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8880';

function App() {
  const [projects, setProjects] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsRes, analyticsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/projects`),
        axios.get(`${API_BASE}/api/analytics/dashboard`)
      ]);
      
      setProjects(projectsRes.data);
      setAnalytics(analyticsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData) => {
    try {
      await axios.post(`${API_BASE}/api/projects`, projectData);
      loadData();
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading IA-Ops Veritas...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🧪 IA-Ops Veritas</h1>
          <p>Testing & Quality Assurance Platform</p>
        </div>
        <nav className="header-nav">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={activeTab === 'projects' ? 'active' : ''}
            onClick={() => setActiveTab('projects')}
          >
            Projects
          </button>
          <a href={process.env.REACT_APP_PORTAL_URL || 'http://localhost:8876'} target="_blank" rel="noopener noreferrer">
            Portal
          </a>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && (
          <Dashboard analytics={analytics} />
        )}
        
        {activeTab === 'projects' && (
          <Projects projects={projects} onCreateProject={createProject} />
        )}
      </main>
    </div>
  );
}

function Dashboard({ analytics }) {
  return (
    <div className="dashboard">
      <h2>📊 Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{analytics.total_projects || 0}</div>
          <div className="stat-label">Total Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.total_executions || 0}</div>
          <div className="stat-label">Test Executions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.total_user_stories || 0}</div>
          <div className="stat-label">User Stories</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.success_rate || 0}%</div>
          <div className="stat-label">Success Rate</div>
        </div>
      </div>

      <div className="dashboard-actions">
        <h3>🚀 Quick Actions</h3>
        <div className="action-buttons">
          <button onClick={() => window.open('http://localhost:8876', '_blank')}>
            📊 Open Portal
          </button>
          <button onClick={() => window.open('http://localhost:8877', '_blank')}>
            📋 Test Results
          </button>
          <button onClick={() => window.open('http://localhost:9899', '_blank')}>
            🗂️ MinIO Console
          </button>
        </div>
      </div>
    </div>
  );
}

function Projects({ projects, onCreateProject }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    repository: '',
    description: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreateProject(formData);
    setFormData({ name: '', repository: '', description: '' });
    setShowForm(false);
  };

  return (
    <div className="projects">
      <div className="projects-header">
        <h2>📊 Projects</h2>
        <button onClick={() => setShowForm(true)}>+ New Project</button>
      </div>

      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <h3>Create New Project</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Project Name:</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Repository URL:</label>
                <input
                  type="url"
                  value={formData.repository}
                  onChange={(e) => setFormData({...formData, repository: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows="3"
                />
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit">Create Project</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card">
            <h3>{project.name}</h3>
            <p>{project.description}</p>
            <div className="project-meta">
              <span className="status">{project.status}</span>
              <span className="date">{new Date(project.created_at).toLocaleDateString()}</span>
            </div>
            <div className="project-actions">
              <button onClick={() => window.open(`http://localhost:8876/service/project_manager`, '_blank')}>
                📊 Manage
              </button>
              <button onClick={() => window.open(`http://localhost:8875`, '_blank')}>
                🔍 Analyze
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
