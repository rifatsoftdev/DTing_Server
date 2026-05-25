import uvicorn
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=get_ip(),
        port=8000,
        reload=True,
        log_level="info",
        # ssl_keyfile="localhost+2-key.pem",
        # ssl_certfile="localhost+2.pem"
    )