export class ApiClient {
    constructor(BASE_URL) {
        this.BASE_URL = BASE_URL;
        this.isRefreshing = false;
        this.refreshPromise = null;
        this.isRedirecting = false; // notun flag
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
            const message = errBody?.message || "";
            
            // SHUDHU "Invalid or Expired Token" hoile refresh
            const shouldRefresh = message === "Invalid or Expired Token" && retry;

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

    async handleTokenRefresh() {
        if (this.isRefreshing) return this.refreshPromise;

        this.isRefreshing = true;
        this.refreshPromise = (async () => {
            try {
                const response = await fetch(this.BASE_URL + "/auth/refresh-access-token", {
                    method: "POST",
                    credentials: "include",
                    headers: { "X-Client-Type": "web" }
                });
                if (!response.ok) throw new Error("Refresh failed");
                return true;
            } catch (err) {
                console.error("Refresh error:", err.message);
                return false;
            } finally {
                this.isRefreshing = false;
            }
        })();
        return this.refreshPromise;
    }

    get(url) { return this.request("GET", url); }
    post(url, body) { return this.request("POST", url, body); }
    put(url, body) { return this.request("PUT", url, body); }
    delete(url, body = null) { return this.request("DELETE", url, body); }
}