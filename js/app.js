// Global Utility Functions
const App = {
    // API Configuration
    API_URL: 'http://localhost:8003',
    SUPABASE_URL: 'https://wrkjqnbpoeplbxnbgggn.supabase.co', 
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indya2pxbmJwb2VwbGJ4bmJnZ2duIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MzI4NDgsImV4cCI6MjA4OTIwODg0OH0.G3b2FIhew9puxSe9rRl81GOBXrZaATa-DNl6bwGHqsY',
    
    // Supabase Client Initialization
    getSupabase() {
        if (!this.supabaseClient) {
            this.supabaseClient = supabase.createClient(this.SUPABASE_URL, this.SUPABASE_ANON_KEY);
        }
        return this.supabaseClient;
    },

    // Check if user is logged in

    isAuthenticated() {
        return !!localStorage.getItem('jwt_token');
    },

    // Handle Logout
    async logout() {
        try {
            await this.getSupabase().auth.signOut();
        } catch(e) {}
        localStorage.removeItem('jwt_token');
        window.location.href = 'login.html';
    },

    // Enforce authentication on protected pages
    requireAuth() {
        const publicPages = ['index.html', 'login.html', 'register.html', ''];
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        if (!this.isAuthenticated() && !publicPages.includes(currentPage)) {
            window.location.href = 'login.html';
        }
        
        if (this.isAuthenticated() && (currentPage === 'login.html' || currentPage === 'register.html' || currentPage === 'index.html')) {
            window.location.href = 'dashboard.html';
        }
    },

    // Show Loading state on button
    setLoading(buttonId, isLoading, text = 'Loading...') {
        const btn = document.getElementById(buttonId);
        if (!btn) return;
        
        if (isLoading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = `<span class="spinner" style="width: 16px; height: 16px; border-width: 2px; margin-right: 8px;"></span> ${text}`;
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.originalText;
            btn.disabled = false;
        }
    },

    // Real API Call helper
    async apiCall(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json'
        };

        const token = localStorage.getItem('jwt_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const options = {
            method,
            headers
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${this.API_URL}${endpoint}`, options);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            throw error;
        }
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    App.requireAuth();

    // Attach logout handlers
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            App.logout();
        });
    });
});
