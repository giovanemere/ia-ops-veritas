// IA-Ops Veritas - Shared JavaScript Utilities

class VeritasUtils {
    static API_BASE = {
        portal: 'http://localhost:8869/api',
        projectManager: 'http://localhost:8874/api',
        repositoryAnalyzer: 'http://localhost:8875/api',
        testManager: 'http://localhost:8870/api',
        executionEngine: 'http://localhost:8871/api',
        qualityAnalytics: 'http://localhost:8872/api',
        evidenceManager: 'http://localhost:8873/api'
    };

    // HTTP Utilities
    static async apiCall(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };

        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    static async get(service, endpoint) {
        const url = `${this.API_BASE[service]}${endpoint}`;
        return this.apiCall(url);
    }

    static async post(service, endpoint, data) {
        const url = `${this.API_BASE[service]}${endpoint}`;
        return this.apiCall(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async put(service, endpoint, data) {
        const url = `${this.API_BASE[service]}${endpoint}`;
        return this.apiCall(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async delete(service, endpoint) {
        const url = `${this.API_BASE[service]}${endpoint}`;
        return this.apiCall(url, { method: 'DELETE' });
    }

    // UI Utilities
    static showLoading(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div style="text-align: center;">
                <div class="loading-spinner"></div>
                <p style="margin-top: 1rem; color: var(--text-primary);">${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    static hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    static showAlert(message, type = 'success') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = message;
        
        // Insert at top of container or body
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alert, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    static showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    static hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // Form Utilities
    static getFormData(formId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    static resetForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }

    // Navigation Utilities
    static updateBreadcrumb(items) {
        const breadcrumb = document.querySelector('.nav-breadcrumb');
        if (breadcrumb) {
            breadcrumb.innerHTML = items.map((item, index) => {
                if (index === items.length - 1) {
                    return `<span>${item.text}</span>`;
                } else {
                    return `<a href="${item.url}">${item.text}</a> <span>/</span>`;
                }
            }).join(' ');
        }
    }

    // Data Formatting
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Table Utilities
    static createTable(data, columns, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const table = document.createElement('table');
        table.className = 'data-table';

        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.label;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                if (col.render) {
                    td.innerHTML = col.render(row[col.key], row);
                } else {
                    td.textContent = row[col.key] || '';
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.innerHTML = '';
        container.appendChild(table);
    }

    // Progress Utilities
    static updateProgress(containerId, percentage) {
        const container = document.getElementById(containerId);
        if (container) {
            const progressBar = container.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${percentage}%`;
            }
        }
    }

    // Tab Utilities
    static initTabs(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const tabButtons = container.querySelectorAll('.tab-button');
        const tabContents = container.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;

                // Remove active class from all buttons and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                const targetContent = container.querySelector(`[data-tab-content="${targetTab}"]`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }

    // Local Storage Utilities
    static saveToStorage(key, data) {
        try {
            localStorage.setItem(`veritas_${key}`, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to storage:', error);
        }
    }

    static loadFromStorage(key) {
        try {
            const data = localStorage.getItem(`veritas_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error loading from storage:', error);
            return null;
        }
    }

    // Validation Utilities
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validateUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
}

// Initialize global utilities when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all tabs on the page
    document.querySelectorAll('.tabs-container').forEach(container => {
        VeritasUtils.initTabs(container.id);
    });

    // Initialize modal close buttons
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Initialize dropdown toggles
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });
        }
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown.active').forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    });
});

// Export for use in other scripts
window.VeritasUtils = VeritasUtils;
