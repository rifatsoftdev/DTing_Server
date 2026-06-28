export class ApiClient {
    constructor(BASE_URL) {
        this.BASE_URL = BASE_URL;
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
            // Network fail, server down, CORS etc. User ke logout kora jabe na
            // console.error("Network error:", networkErr);
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

        // console.log(data.status_code);
        // console.log(data.message);

        // 1. Success case
        if (response.ok) {
            return data;
        }
        
        // 2. 401 Unauthorized - token issue kina check koro
        if (response.status === 401) {
            const message = data?.message || data?.detail || "";
            const isTokenExpired = message === "Invalid or Expired Token" || message === "Token expired" || message === "Missing authentication token";
            
            // console.log(message)
            // console.log(isTokenExpired)

            // Khali token expired hoile + auth endpoint na hoile + retry true hoile refresh
            if (isTokenExpired && retry && !this.isAuthEndpoint(url)) {
                const refreshed = await this.handleTokenRefresh();
                if (refreshed) {
                    return this.request(method, url, body, false); // ekbar e retry
                }
                // Refresh fail hoile niche logout hobe
            }

            // Token invalid/expired ar refresh o fail, taholei logout
            if (isTokenExpired) {
                // this.forceLogout();
            }
            
            throw new Error(message || "Authentication failed");
        }

        // 3. 403 Forbidden - permission nai, logout na
        // 4. 500, 502, 503 - server error, logout na
        // 5. Baki sob error - just message throw koro
        const errorMessage = data?.message || data?.detail || `HTTP Error ${response.status}`;
        throw new Error(errorMessage);
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

                const response = await fetch(this.BASE_URL + "/auth/refresh-access-token", {
                    method: "POST",
                    credentials: "include",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-Client-Type": "web" 
                    },
                    body: JSON.stringify(body)
                });
                
                // Refresh API 500 dileo logout korbo na. Just false return korbo
                if (!response.ok) {
                    console.error("Refresh API failed with status:", response.status);
                    return false;
                }
                
                return true;
            } catch (err) {
                // Network error hoileo logout na
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
        // Ei function ta khali tokhoni call hobe jokhon sure token invalid
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