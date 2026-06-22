export class ApiClient {
    constructor(BASE_URL) {
        this.BASE_URL = BASE_URL;
        this.isRefreshing = false;
        this.refreshPromise = null;
    }

    // ======================
    // Core request handler
    // ======================
    async request(method, url, body = null, retry = true) {
        const options = {
            method,
            credentials: "include",      // cookie pathano/grohon korar jonno MUST
            headers: {
                "Content-Type": "application/json",
                "X-Client-Type": "web"   // backend ke client type bujhano
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(this.BASE_URL + url, options);

        // ======================
        // Handle 401 - error_code dekhe decide kora
        // ======================
        if (response.status === 401) {
            const errBody = await response.json().catch(() => ({}));
            const errorCode = errBody?.data?.error_code;

            // SHUDHU token expired hole refresh try korbe
            if (errorCode === "TOKEN_EXPIRED" && retry) {
                const refreshed = await this.handleTokenRefresh();

                if (refreshed) {
                    return this.request(method, url, body, false);   // notun cookie diye ekbar retry
                }
            }

            // TOKEN_MISSING / DEVICE_MISMATCH / refresh fail / retry already use hoyeche
            // -> shorashori login e pathiye dewa, refresh try korar dorkar nei
            console.warn("Auth failed:", errorCode || errBody?.message);
            window.location.href = "/login";
            
            return null;
        }

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(errText || `HTTP Error: ${response.status}`);
        }

        return await response.json();
    }

    // ======================
    // Token Refresh System
    // ======================
    async handleTokenRefresh() {
        if (this.isRefreshing) {
            return this.refreshPromise;
        }

        this.isRefreshing = true;

        this.refreshPromise = (async () => {
            try {
                // refresh_token cookie (HttpOnly, path=/api/auth/refresh) browser
                // nijei pathabe - body e kichu pathanor dorkar nei
                const response = await fetch(this.BASE_URL + "/auth/refresh-access-token", {
                    method: "POST",
                    credentials: "include",
                    headers: { "X-Client-Type": "web" }
                });

                if (!response.ok) {
                    throw new Error("Refresh token failed");
                }

                // backend notun access_token cookie already set kore diyeche
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

    // ======================
    // Shortcut methods
    // ======================
    get(url) {
        return this.request("GET", url);
    }

    post(url, body) {
        return this.request("POST", url, body);
    }

    put(url, body) {
        return this.request("PUT", url, body);
    }

    delete(url, body = null) {
        return this.request("DELETE", url, body);
    }
}