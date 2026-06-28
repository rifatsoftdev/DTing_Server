export class ApiClient {
    constructor(BASE_URL) {
        this.BASE_URL = BASE_URL;
        this.AUTH_URL = BASE_URL;
        this.isRefreshing = false;
        this.refreshPromise = null;
        this.isRedirecting = false;
    }

    async request(method, url, body = null, retry = true) {
        const options = {
            method,
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-Client-Type": "web"
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        let response;
        try {
            response = await fetch(this.BASE_URL + url, options);
        } catch (networkErr) {
            throw new Error("Network error. Please check your connection.");
        }

        let data = null;
        const contentType = response.headers.get("content-type");
        
        if (contentType && contentType.includes("application/json")) {
            try {
                data = await response.json();
            } catch {
                data = null;
            }
        }

        // 401 Unauthorized - token issue handle
        if (response.status === 401) {
            const message = (data?.message || data?.detail || "").toLowerCase();
            const isTokenExpired = message.includes("token") && (message.includes("expired") || message.includes("invalid") || message.includes("missing"));

            if (isTokenExpired && retry && !this.isAuthEndpoint(url)) {
                const refreshed = await this.handleTokenRefresh();

                if (refreshed) {
                    return this.request(method, url, body, false); // একবার retry
                }
                // Refresh fail হলে logout
                // this.forceLogout(); 
            }
            
            const error = new Error(data?.message || data?.detail || "Authentication failed");
            error.data = data;
            error.status = response.status;
            throw error;
        }

        // Success case
        if (response.ok) {
            return data;
        }

        // বাকি সব error - 403, 404, 400, 500 etc
        const errorMessage = data?.message || data?.detail || `HTTP Error ${response.status}`;
        const error = new Error(errorMessage);
        error.data = data; // backend থেকে আসা action, status_code সব থাকবে
        error.status = response.status;
        throw error;
    }

    isAuthEndpoint(url) {
        return url.includes("/auth/login")
            || url.includes("/auth/signin")
            || url.includes("/auth/logout")
            || url.includes("/auth/refresh-access-token")
            || url.includes("/auth/new-access-token");
    }

    async handleTokenRefresh() {
        if (this.isRefreshing) return this.refreshPromise;
        this.isRefreshing = true;
        
        this.refreshPromise = (async () => {
            try {
                const body = {
                    user_id: localStorage.getItem('user_id'),
                    device_id: localStorage.getItem('device_id'),
                    device_uuid: localStorage.getItem('device_uuid')
                };

                const response = await fetch(this.AUTH_URL + "/auth/refresh-access-token", {
                    method: "POST",
                    credentials: "include",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-Client-Type": "web" 
                    },
                    body: JSON.stringify(body)
                });
                
                if (!response.ok) {
                    console.error("Refresh API failed with status:", response.status);
                    return false;
                }
                
                return true;
            } catch (err) {
                console.error("Refresh network error:", err.message);
                return false;
            } finally {
                this.isRefreshing = false;
                this.refreshPromise = null;
            }
        })();
        return this.refreshPromise;
    }

    forceLogout() {
        if (this.isRedirecting) return;
        
        localStorage.removeItem("user_id");
        localStorage.removeItem("device_id");
        localStorage.removeItem("device_uuid");

        const isLoginPage = window.location.pathname.includes("login");
        if (!isLoginPage) {
            this.isRedirecting = true;
            window.location.href = "/user/user_login.html";
        }
    }

    get(url) { return this.request("GET", url); }
    post(url, body) { return this.request("POST", url, body); }
    put(url, body) { return this.request("PUT", url, body); }
    delete(url, body = null) { return this.request("DELETE", url, body); }
}