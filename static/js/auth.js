import { get_device_id, get_device_uuid } from './utils.js';

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
            message = "Server returned HTML instead of JSON.";
        } else if (raw) {
            message = raw;
        }
    }
    return message;
}

async function verifyNewUserEmail({ user_id, otp, email_verification_token }) {
    const device_id = get_device_id();
    const device_uuid = await get_device_uuid();
    
    const response = await fetch(`${window.location.origin}/auth/verify-new-user-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id,
            otp,
            email_verification_token,
            device_id,
            device_uuid
        })
    });
    
    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};
    
    if (!response.ok) {
        throw new Error(data?.message || data?.detail || "Verification failed");
    }
    
    return data;
}

async function verifyOTP({ method, delever_to, otp, otp_token }) {
    const device_id = get_device_id();
    const device_uuid = await get_device_uuid();
    
    const response = await fetch(`${window.location.origin}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            method,
            delever_to,
            otp,
            otp_token,
            device: "web",
            device_id,
            device_uuid
        })
    });
    
    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};
    
    if (!response.ok) {
        throw new Error(data?.message || data?.detail || "OTP verification failed");
    }
    
    return data;
}

async function sendOTP({ method, delever_to }) {
    const device_id = get_device_id();
    const device_uuid = await get_device_uuid();
    
    const response = await fetch(`${window.location.origin}/auth/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            method,
            delever_to,
            device: "web",
            device_id,
            device_uuid
        })
    });
    
    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};
    
    if (!response.ok) {
        throw new Error(data?.message || data?.detail || "Failed to send OTP");
    }
    
    return data;
}

async function resendNewUserEmailVerification({ email_verification_token, delever_to }) {
    const device_id = get_device_id();
    const device_uuid = await get_device_uuid();
    
    const response = await fetch(`${window.location.origin}/auth/resend-verification-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email_verification_token,
            email: delever_to,
            device_id,
            device_uuid
        })
    });
    
    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};
    
    if (!response.ok) {
        throw new Error(data?.message || data?.detail || "Failed to resend verification");
    }
    
    return data;
}

function persistAuthSession({ user_id, access_token, refresh_token }) {
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

window.verifyNewUserEmail = verifyNewUserEmail;
window.verifyOTP = verifyOTP;
window.sendOTP = sendOTP;
window.resendNewUserEmailVerification = resendNewUserEmailVerification;
window.persistAuthSession = persistAuthSession;