let offerModal;
let offersCache = [];

document.addEventListener("DOMContentLoaded", () => {
    offerModal = getOfferModal();
    loadOffers();
});

function getOfferModal() {
    const modalElement = document.getElementById("offerModal");
    if (!modalElement || !window.bootstrap) {
        return null;
    }

    offerModal = bootstrap.Modal.getOrCreateInstance(modalElement);
    return offerModal;
}

function parseJsonField(elementId) {
    const value = document.getElementById(elementId).value.trim();
    if (!value) {
        return null;
    }

    try {
        return JSON.parse(value);
    } catch (error) {
        throw new Error(`${elementId === "offerTargetUser" ? "Target User" : "Meta Data"} must be valid JSON`);
    }
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function toDateTimeLocal(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return "";
    }

    const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return offsetDate.toISOString().slice(0, 16);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function loadOffers() {
    const tbody = document.getElementById("offersTableBody");
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5">Loading offers...</td></tr>';

    try {
        const response = await fetch("/offer/offers?include_expired=true", {
            method: "GET",
            headers: { ...Auth.getAuthHeader() },
            credentials: "include"
        });

        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(result.detail || result.message || "Failed to load offers");
        }

        offersCache = result.data.offers || [];

        if (offersCache.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5">No offers found.</td></tr>';
            return;
        }

        tbody.innerHTML = "";
        offersCache.forEach((offer) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>
                    <img class="offer-thumb" src="${escapeHtml(offer.image_url)}" alt="${escapeHtml(offer.title)}">
                </td>
                <td class="offer-title-cell">
                    <strong>${escapeHtml(offer.title)}</strong>
                    <div class="text-muted small">ID: ${offer.id}</div>
                </td>
                <td>${escapeHtml(offer.description)}</td>
                <td>${formatDateTime(offer.expires_at)}</td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-info" type="button" onclick="editOffer(${offer.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" type="button" onclick="deleteOffer(${offer.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error("Failed to load offers:", error);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5 text-danger">Error loading offers.</td></tr>';
        showToast(error.message || "Failed to load offers", "error");
    }
}

function showAddOfferModal() {
    document.getElementById("offerModalTitle").innerText = "Add New Offer";
    document.getElementById("offerForm").reset();
    document.getElementById("offerId").value = "";
    getOfferModal()?.show();
}

function editOffer(offerId) {
    const offer = offersCache.find((item) => item.id === offerId);
    if (!offer) {
        showToast("Offer not found", "error");
        return;
    }

    document.getElementById("offerModalTitle").innerText = "Edit Offer";
    document.getElementById("offerId").value = offer.id;
    document.getElementById("offerImageUrl").value = offer.image_url || "";
    document.getElementById("offerTitle").value = offer.title || "";
    document.getElementById("offerDescription").value = offer.description || "";
    document.getElementById("offerExpiresAt").value = toDateTimeLocal(offer.expires_at);
    document.getElementById("offerTargetUser").value = offer.target_user ? JSON.stringify(offer.target_user, null, 2) : "";
    document.getElementById("offerMetaData").value = offer.meta_data ? JSON.stringify(offer.meta_data, null, 2) : "";

    getOfferModal()?.show();
}

async function saveOffer() {
    try {
        const form = document.getElementById("offerForm");
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const offerId = document.getElementById("offerId").value;
        const isEdit = Boolean(offerId);

        const payload = {
            image_url: document.getElementById("offerImageUrl").value.trim(),
            title: document.getElementById("offerTitle").value.trim(),
            description: document.getElementById("offerDescription").value.trim(),
            target_user: parseJsonField("offerTargetUser"),
            meta_data: parseJsonField("offerMetaData"),
            expires_at: document.getElementById("offerExpiresAt").value
        };

        if (isEdit) {
            payload.offer_id = Number(offerId);
        }

        const response = await fetch(isEdit ? "/offer/edit-offer" : "/offer/add-offer", {
            method: isEdit ? "PUT" : "POST",
            headers: {
                "Content-Type": "application/json",
                ...Auth.getAuthHeader()
            },
            credentials: "include",
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(result.detail || result.message || "Failed to save offer");
        }

        showToast(isEdit ? "Offer updated successfully" : "Offer added successfully", "success");
        getOfferModal()?.hide();
        loadOffers();
    } catch (error) {
        showToast(error.message || "Failed to save offer", "error");
    }
}

async function deleteOffer(offerId) {
    if (!window.confirm("Delete this offer?")) {
        return;
    }

    try {
        const response = await fetch(`/offer/delete-offer/${offerId}`, {
            method: "DELETE",
            headers: { ...Auth.getAuthHeader() },
            credentials: "include"
        });

        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(result.detail || result.message || "Failed to delete offer");
        }

        showToast("Offer deleted successfully", "success");
        loadOffers();
    } catch (error) {
        showToast(error.message || "Failed to delete offer", "error");
    }
}
