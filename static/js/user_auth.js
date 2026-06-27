import { get_device_id, get_device_uuid } from './utils.js';
import { ApiClient } from "./ApiClient.js";


// api.get("/users").then(data => {
//     console.log(data);
// });


// Website base url
const BASE_URL = window.location.origin;
const api = new ApiClient(BASE_URL);


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
export async function loginUser(api, {
    email_address = null,
    phone_number = null,
    country_code = null,
    user_password
}) {
    const device_id = get_device_id();
    const device_uuid = await get_device_uuid();

    // console.log(typeof device_id)
    // console.log(typeof device_uuid)

    const payload = {
        email_address,
        phone_number,
        country_code,
        user_password,
        device_id,
        device_uuid
    };

    console.log(payload);

    try {
        const responce = await api.post("/auth/login", payload);

        const action = responce?.action;
        const data = responce?.data;

        if (action === "login") {
            // ✅ Cookie already backend e set hoye gেছে (HttpOnly access_token + refresh_token)
            // localStorage ba api.setTokens() kichui lagbe na - browser nijei cookie pathabe
            console.log("login");
            
            // save locally
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('device_id', data.device_id);
            localStorage.setItem('device_uuid', data.device_uuid);

            window.location.href = "/account";
        }

        else if (action === "2fa_verification_required") {
            console.log("2fa_verification_required");
            window.location.href = `/otp.html?user_id=${data.user_id}`;
        }

        else if (action === "verify_email") {
            console.log("verify_email");
            window.location.href = `/verify-email.html?email=${result.email_address}`;
        }

        else {
            console.warn("Unknown action:", action);
        }

    } catch (error) {
        console.error("Login error:", error.message);
        throw error;
    }
}

async function sendOTP({
    method,
    delever_to
}) {
    const url = `${BASE_URL}/auth/send-otp`;

    const device_id = get_device_id();
    const device_uuid = get_device_uuid();

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
    const device_id = get_device_id();
    const device_uuid = get_device_uuid();
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

