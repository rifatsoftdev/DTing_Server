export class ApiClient {
    constructor(BASE_URL) {
        this.BASE_URL = BASE_URL;
        this.isRefreshing = false;
        this.refreshPromise = null;
        this.isRedirecting = false; // notun flag
        this.user_id = localStorage.getItem('user_id');
        this.device_id = localStorage.getItem('device_id');
        this.device_uuid = localStorage.getItem('device_uuid');
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

        const response = await fetch(this.BASE_URL + url, options);

        if (response.status === 401) {
            const errBody = await response.json().catch(() => ({}));
            const message = errBody?.message || errBody?.detail || "";
            
            const shouldRefresh = retry && !this.isAuthEndpoint(url);

            if (shouldRefresh) {
                const refreshed = await this.handleTokenRefresh();
                if (refreshed) {
                    return this.request(method, url, body, false); // 1 bar retry
                }
            }

            // *** MAIN FIX: Loop atkate ***
            // 1. Already login page e thakle redirect korbo na
            // 2. Ekbar redirect shuru hoile ar korbo na
            const isLoginPage = window.location.pathname === "/login";
            if (!isLoginPage && !this.isRedirecting) {
                this.isRedirecting = true;
                console.warn("Auth failed:", message);
                window.location.href = "/login";
            }
            
            return null;
        }

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(errText || `HTTP Error: ${response.status}`);
        }

        return await response.json();
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
                    user_id: localStorage.getItem('user_id') || this.user_id,
                    device_id: localStorage.getItem('device_id') || this.device_id,
                    device_uuid: localStorage.getItem('device_uuid') || this.device_uuid
                };

                const response = await fetch(this.BASE_URL + "/auth/refresh-access-token", {
                    method: "POST",
                    credentials: "include", // cookie auto jabe
                    headers: { 
                        "Content-Type": "application/json",
                        "X-Client-Type": "web" 
                    },
                    body: JSON.stringify(body)
                });
                if (!response.ok) throw new Error("Refresh failed");
                await response.json();
                return true;
            } catch (err) {
                console.error("Refresh error:", err.message);
                this.logout();
                return false;
            } finally {
                this.isRefreshing = false;
            }
        })();
        return this.refreshPromise;
    }

    logout() {
        localStorage.removeItem("user_id");
        localStorage.removeItem("device_id");
        localStorage.removeItem("device_uuid");

        if (!this.isRedirecting && window.location.pathname !== "/login") {
            this.isRedirecting = true;
            window.location.href = "/login";
        }
    }

    get(url) { return this.request("GET", url); }
    post(url, body) { return this.request("POST", url, body); }
    put(url, body) { return this.request("PUT", url, body); }
    delete(url, body = null) { return this.request("DELETE", url, body); }
}
