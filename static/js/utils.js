// UUID generator (safe fallback included)
function safeUUID() {
  if (window.crypto && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// device_id (stored permanently in localStorage)
export function get_device_id() {
  let device_id = localStorage.getItem("device_id");

  if (!device_id) {
    device_id = safeUUID();
    localStorage.setItem("device_id", device_id);
  }

  return device_id;
}

// device_uuid (currently fallback to device_id until backend ready)
export async function get_device_uuid() {
  let device_uuid = localStorage.getItem("device_uuid");

  if (!device_uuid) {
    const device_id = get_device_id();

    // 🔥 backend API not ready yet → fallback
    device_uuid = device_id;

    localStorage.setItem("device_uuid", device_uuid);
  }

  return device_uuid;
}