/**
 * PocketPay Admin Authentication Handler
 * Manages login, logout, and session management
 */

// Auth state
class AuthService {
    constructor() {
        this.refreshPromise = null;
    }

    getDeviceId() {
        let deviceId = localStorage.getItem("admin_device_id");
        if (!deviceId) {
            deviceId = "web_admin_panel";
            localStorage.setItem("admin_device_id", deviceId);
        }
        return deviceId;
    }

    getDeviceUuid() {
        let deviceUuid = localStorage.getItem("admin_device_uuid");
        if (!deviceUuid) {
            deviceUuid = crypto.randomUUID ? crypto.randomUUID() : `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
            localStorage.setItem("admin_device_uuid", deviceUuid);
        }
        return deviceUuid;
    }

    // admin login
    async login(email, password) {
        try {
            showLoading();
            const deviceId = this.getDeviceId();
            const deviceUuid = this.getDeviceUuid();

            const response = await fetch(`/admin/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    email,
                    password,
                    device_id: deviceId,
                    device_uuid: deviceUuid
                })
            });

            if (response.status === 200) {
                const data = await response.json();

                if (data.success) {
                    // Save tokens and non-sensitive info in localStorage
                    localStorage.setItem('admin_id', data.data.admin_id);
                    localStorage.setItem('admin_access_token', data.data.access_token);
                    localStorage.setItem('admin_refresh_token', data.data.refresh_token);
                    localStorage.setItem('admin_device_id', deviceId);
                    localStorage.setItem('admin_device_uuid', deviceUuid);
                    
                    showToast('Login successful!', 'success');

                    setTimeout(() => {
                        window.location.href = '/admin/dashboard';
                    }, 500);

                    return true;
                }

                showLoginErrorDialog(data.message || 'Login failed');
                return false;
            } else if (response.status === 404) {
                showToast('Admin account not found', 'error');
                // showLoginErrorDialog('Admin account not found');
                return false;
            } else if (response.status === 401) {
                showLoginErrorDialog('Invalid email or password');
                return false;
            } 

            showLoginErrorDialog('Login failed');
            return false;
        } catch (error) {
            console.error(error);
            showLoginErrorDialog('Login error');
            return false;
        } finally {
            hideLoading();
        }
    }

    // admin logout
    async logout() {
        try {
            await fetch("/admin/logout", {
                method: "POST",
                credentials: "include"
            });

        } finally {
            localStorage.clear();
            window.location.href = "/admin/login";
        }
    }

    // get new access token
    async getAccessToken() {
        const refreshToken = localStorage.getItem("admin_refresh_token");
        if (!refreshToken) return null;

        if (this.refreshPromise) {
            return this.refreshPromise;
        }

        this.refreshPromise = this.refreshAccessToken(refreshToken);

        try {
            return await this.refreshPromise;
        } finally {
            this.refreshPromise = null;
        }
    }

    async refreshAccessToken(refreshToken) {
        const response = await window.__rawFetch("/admin/refresh-access-token", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                refresh_token: refreshToken,
                device_id: this.getDeviceId(),
                device_uuid: this.getDeviceUuid()
            })
        });

        let data = null;
        try {
            data = await response.json();
        } catch (error) {
            return null;
        }

        if (response.ok && data.success) {
            localStorage.setItem("admin_access_token", data.data.access_token);
            localStorage.setItem("admin_refresh_token", data.data.refresh_token);
            return data.data.access_token;
        }
        return null;
    }

    // check login
    isLoggedIn() {
        return !!localStorage.getItem("admin_id");
    }

    // get auth header for API calls
    getAuthHeader() {
        // First try to get from localStorage (if refreshed)
        let token = localStorage.getItem("admin_access_token");
        
        // If not in localStorage, try to get from cookie
        if (!token) {
            token = this.getCookie("admin_access_token");
        }
        
        if (token) {
            return { "Authorization": `Bearer ${token}` };
        }
        return {};
    }

    // fetch with automatic access-token refresh and one retry
    async authFetch(input, options = {}) {
        if (this.isAuthEndpoint(input)) {
            return window.__rawFetch(input, options);
        }

        const response = await window.__rawFetch(input, this.withAuthHeader(options));

        if (response.status !== 401) {
            return response;
        }

        const newAccessToken = await this.getAccessToken();
        if (!newAccessToken) {
            await this.logout();
            return response;
        }

        return window.__rawFetch(input, this.withAuthHeader(options, newAccessToken));
    }

    withAuthHeader(options = {}, token = null) {
        const headers = new Headers(options.headers || {});
        const accessToken = token || localStorage.getItem("admin_access_token") || this.getCookie("admin_access_token");

        if (accessToken) {
            headers.set("Authorization", `Bearer ${accessToken}`);
        }

        return {
            ...options,
            headers
        };
    }

    isAuthEndpoint(input) {
        const url = typeof input === "string" ? input : input?.url || "";
        return url.includes("/admin/login")
            || url.includes("/admin/logout")
            || url.includes("/admin/refresh-access-token");
    }

    // get cookie value
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
}

// Global auth instance used by templates
window.__rawFetch = window.__rawFetch || window.fetch.bind(window);
const Auth = new AuthService();
window.fetch = function(input, options = {}) {
    return Auth.authFetch(input, options);
};



// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    // For login page
    if (window.location.pathname.includes('login.html') || window.location.pathname.endsWith('/admin/login') || window.location.pathname.includes('admin_login')) {
        setupLoginForm();
    }
});

// Setup login form
function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async function(e) {
        // Prevent default form submission - this ensures credentials are NOT sent as URL params
        e.preventDefault();
        e.stopPropagation();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('errorMessage');
        
        // Basic validation
        if (!email || !password) {
            showError('Please enter both email and password');
            return;
        }
        
        // Hide any previous error
        errorMsg.style.display = 'none';
        
        // Attempt login - credentials are sent in request body, NOT in URL
        const result = await Auth.login(email, password);
        
        if (!result) {
            showError('Login failed');
        }
    });
}

// Show error message
function showError(message) {
    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) {
        errorMsg.querySelector('span').textContent = message;
        errorMsg.style.display = 'flex';
    }
}

// Show loading state on button
function showLoading() {
    const btn = document.querySelector('#loginForm .btn[type="submit"]');
    if (btn) {
        btn.disabled = true;
        btn.querySelector('.btn-text').style.display = 'none';
        btn.querySelector('.btn-loader').style.display = 'inline-block';
    }
}

// Hide loading state on button
function hideLoading() {
    const btn = document.querySelector('#loginForm .btn[type="submit"]');
    if (btn) {
        btn.disabled = false;
        btn.querySelector('.btn-text').style.display = 'inline';
        btn.querySelector('.btn-loader').style.display = 'none';
    }
}

// Close modal
function closeModal() {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('modal');
    if (overlay) overlay.style.display = 'none';
    if (modal) modal.style.display = 'none';
}

// Show login error dialog
function showLoginErrorDialog(message) {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('modal');

    if (overlay && modal) {
        modal.innerHTML = `
            <div class="modal-header">
                <h2><i class="fas fa-exclamation-triangle"></i> Login Failed</h2>
                <button class="modal-close" onclick="closeModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="error-message-dialog">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="closeModal()">
                        Try Again
                    </button>
                </div>
            </div>
        `;

        overlay.style.display = 'block';
        modal.style.display = 'block';
        modal.focus();
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}
