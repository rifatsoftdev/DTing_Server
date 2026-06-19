

export function get_device_id() {
  let device_id = localStorage.getItem("device_id");

  if (!device_id) {
    device_id = crypto.randomUUID();
    localStorage.setItem("device_id", device_id);
  }

  return device_id;
}

export async function get_device_uuid() {
  let device_uuid = localStorage.getItem("device_uuid");

  if (!device_uuid) {
    const device_id = get_device_id();

    const res = await fetch("/api/device/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        device_id: device_id
      })
    });

    const data = await res.json();

    device_uuid = data.device_uuid;

    localStorage.setItem("device_uuid", device_uuid);
  }

  return device_uuid;
}