const BASE_URL = window.location.origin;

function resolveDeviceIdentity() {
    const device_id = (typeof getDeviceId === "function") ? getDeviceId() : "web_device_id";
    const device_uuid = (typeof getDeviceUuid === "function") ? getDeviceUuid() : "web_device_uuid";
    return { device_id, device_uuid };
}

async function parseResponseError(response) {
    let message = "Request failed";
    const raw = await response.text();

    try {
        const payload = raw ? JSON.parse(raw) : null;
        if (typeof payload?.detail === "string") {
            message = payload.detail;
        } else if (typeof payload?.message === "string") {
            message = payload.message;
        } else if (Array.isArray(payload?.detail) && payload.detail[0]?.msg) {
            message = payload.detail[0].msg;
        } else if (raw) {
            message = raw;
        }
    } catch (_) {
        if (raw && raw.trim().startsWith("<")) {
            message = "Server returned HTML instead of JSON. Check API route/server error.";
        } else if (raw) {
            message = raw;
        }
    }
    return message;
}

// login with email/phone + password
async function loginUser({
    email_address = null,
    phone_number = null,
    country_code = null,
    user_password
}) {
    const url = `${BASE_URL}/auth/login`;
    const { device_id, device_uuid } = resolveDeviceIdentity();
    const data = {
        email_address,
        phone_number,
        country_code,
        user_password,
        device: "web",
        device_id,
        device_uuid
    };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const message = await parseResponseError(response);
        throw new Error(message);
    }
    const raw = await response.text();
    try {
        return raw ? JSON.parse(raw) : {};
    } catch (_) {
        throw new Error("Server returned non-JSON response. Check backend logs/routes.");
    }
}

async function sendOTP({
    method,
    delever_to
}) {
    const url = `${BASE_URL}/auth/send-otp`;
    const { device_id, device_uuid } = resolveDeviceIdentity();
    const data = {
        method,
        delever_to,
        device: "web",
        device_id,
        device_uuid
    };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const message = await parseResponseError(response);
        throw new Error(message);
    }

    const raw = await response.text();
    try {
        return raw ? JSON.parse(raw) : {};
    } catch (_) {
        throw new Error("Server returned non-JSON response. Check backend logs/routes.");
    }
}

async function verifyOTP({
    method,
    delever_to,
    otp,
    otp_token
}) {
    const url = `${BASE_URL}/auth/verify-otp`;
    const { device_id, device_uuid } = resolveDeviceIdentity();
    const data = {
        method,
        delever_to,
        otp,
        otp_token,
        device: "web",
        device_id,
        device_uuid
    };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const message = await parseResponseError(response);
        throw new Error(message);
    }

    const raw = await response.text();
    try {
        return raw ? JSON.parse(raw) : {};
    } catch (_) {
        throw new Error("Server returned non-JSON response. Check backend logs/routes.");
    }
}

async function verifyNewUserEmail({
    user_id,
    otp,
    email_verification_token
}) {
    const url = `${BASE_URL}/auth/verify-new-user-email`;
    const { device_id, device_uuid } = resolveDeviceIdentity();
    const data = {
        user_id,
        otp,
        email_verification_token,
        device_id,
        device_uuid
    };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const message = await parseResponseError(response);
        throw new Error(message);
    }

    const raw = await response.text();
    try {
        return raw ? JSON.parse(raw) : {};
    } catch (_) {
        throw new Error("Server returned non-JSON response. Check backend logs/routes.");
    }
}

async function resendNewUserEmailVerification({
    email_verification_token
}) {
    const url = `${BASE_URL}/auth/resend-verification-email`;
    const data = { email_verification_token };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const message = await parseResponseError(response);
        throw new Error(message);
    }

    const raw = await response.text();
    try {
        return raw ? JSON.parse(raw) : {};
    } catch (_) {
        throw new Error("Server returned non-JSON response. Check backend logs/routes.");
    }
}

function persistAuthSession({
    user_id,
    access_token,
    refresh_token
}) {
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    const oneDay = 60 * 60 * 24;
    const thirtyDays = 60 * 60 * 24 * 30;

    if (user_id) {
        document.cookie = `user_id=${encodeURIComponent(user_id)}; path=/; max-age=${thirtyDays}; SameSite=Lax${secure}`;
        localStorage.setItem("user_id", user_id);
    }
    if (access_token) {
        document.cookie = `access_token=${encodeURIComponent(access_token)}; path=/; max-age=${oneDay}; SameSite=Lax${secure}`;
        localStorage.setItem("access_token", access_token);
    }
    if (refresh_token) {
        document.cookie = `refresh_token=${encodeURIComponent(refresh_token)}; path=/; max-age=${thirtyDays}; SameSite=Lax${secure}`;
        localStorage.setItem("refresh_token", refresh_token);
    }
}
