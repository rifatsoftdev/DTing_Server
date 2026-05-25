function getDeviceId() {
    let id = localStorage.getItem("device_id");
    if (!id) {
        id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : `device_${Date.now()}`;
        localStorage.setItem("device_id", id);
    }
    return id;
}

function getDeviceUuid() {
    let id = localStorage.getItem("device_uuid");
    if (!id) {
        id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : `uuid_${Date.now()}`;
        localStorage.setItem("device_uuid", id);
    }
    return id;
}