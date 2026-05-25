(function () {
    const DIALOG_STYLE_ID = "dting-dialog-style";

    const THEME = {
        success: {
            title: "Success",
            icon: "check",
            color: "#13d8c4"
        },
        error: {
            title: "Error",
            icon: "error",
            color: "#ff6b6b"
        },
        warning: {
            title: "Warning",
            icon: "warning",
            color: "#f59e0b"
        }
    };

    function injectStyles() {
        if (document.getElementById(DIALOG_STYLE_ID)) {
            return;
        }

        const style = document.createElement("style");
        style.id = DIALOG_STYLE_ID;
        style.textContent = `
            .dting-dialog-overlay {
                position: fixed;
                inset: 0;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 16px;
                background: rgba(3, 8, 20, 0.72);
                backdrop-filter: blur(4px);
                animation: dtingDialogFade 0.18s ease;
            }

            .dting-dialog-box {
                width: min(460px, 100%);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.14);
                background:
                    linear-gradient(150deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.015)),
                    rgba(10, 16, 28, 0.92);
                color: #e6edf7;
                box-shadow: 0 28px 64px rgba(0, 0, 0, 0.5);
                transform: translateY(6px) scale(0.98);
                animation: dtingDialogUp 0.22s ease forwards;
                overflow: hidden;
            }

            .dting-dialog-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                padding: 18px 18px 10px;
            }

            .dting-dialog-title-wrap {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .dting-dialog-icon {
                width: 34px;
                height: 34px;
                border-radius: 999px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(255, 255, 255, 0.08);
                flex-shrink: 0;
            }

            .dting-dialog-title {
                margin: 0;
                font-size: 1.04rem;
                font-weight: 700;
                letter-spacing: 0.2px;
            }

            .dting-dialog-close {
                border: 0;
                background: transparent;
                color: #9fb0c6;
                font-size: 1.1rem;
                line-height: 1;
                width: 30px;
                height: 30px;
                border-radius: 8px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background-color 0.18s ease, color 0.18s ease;
            }

            .dting-dialog-close:hover {
                background: rgba(255, 255, 255, 0.08);
                color: #e6edf7;
            }

            .dting-dialog-body {
                padding: 6px 18px 18px;
                color: #ced9e8;
                line-height: 1.6;
                font-size: 0.96rem;
                word-wrap: break-word;
            }

            .dting-dialog-footer {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                padding: 0 18px 18px;
            }

            .dting-dialog-btn {
                border: 0;
                border-radius: 11px;
                padding: 9px 16px;
                font-weight: 700;
                color: #04101d;
                cursor: pointer;
                transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
            }

            .dting-dialog-btn:hover {
                transform: translateY(-1px);
                filter: brightness(1.03);
            }

            .dting-dialog-btn:active {
                transform: translateY(0);
            }

            @keyframes dtingDialogFade {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes dtingDialogUp {
                from { opacity: 0; transform: translateY(8px) scale(0.98); }
                to { opacity: 1; transform: translateY(0) scale(1); }
            }
        `;

        document.head.appendChild(style);
    }

    function iconSvg(type, color) {
        if (type === "check") {
            return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20 7L10 17L5 12" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
        }

        if (type === "warning") {
            return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 8V13" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/><circle cx="12" cy="17" r="1.3" fill="${color}"/><path d="M10.29 3.86L1.82 18A2 2 0 003.53 21H20.47A2 2 0 0022.18 18L13.71 3.86A2 2 0 0010.29 3.86Z" stroke="${color}" stroke-width="2"/></svg>`;
        }

        return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="${color}" stroke-width="2.2"/><path d="M12 8V13" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/><circle cx="12" cy="16.8" r="1.2" fill="${color}"/></svg>`;
    }

    function closeDialog(overlay, onClose) {
        if (!overlay || !overlay.parentNode) {
            return;
        }

        overlay.remove();
        document.body.style.removeProperty("overflow");

        if (typeof onClose === "function") {
            onClose();
        }
    }

    function show(type, message, options = {}) {
        injectStyles();

        const skin = THEME[type] || THEME.success;
        const title = options.title || skin.title;
        const buttonText = options.buttonText || "OK";
        const closeOnOverlay = options.closeOnOverlay !== false;

        const overlay = document.createElement("div");
        overlay.className = "dting-dialog-overlay";

        const dialog = document.createElement("div");
        dialog.className = "dting-dialog-box";
        dialog.setAttribute("role", "dialog");
        dialog.setAttribute("aria-modal", "true");

        dialog.innerHTML = `
            <div class="dting-dialog-header">
                <div class="dting-dialog-title-wrap">
                    <span class="dting-dialog-icon" style="box-shadow: inset 0 0 0 1px ${skin.color}55;">${iconSvg(skin.icon, skin.color)}</span>
                    <h2 class="dting-dialog-title" style="color:${skin.color};">${title}</h2>
                </div>
                <button type="button" class="dting-dialog-close" aria-label="Close">&#10005;</button>
            </div>
            <div class="dting-dialog-body"></div>
            <div class="dting-dialog-footer">
                <button type="button" class="dting-dialog-btn" style="background:${skin.color}; box-shadow: 0 10px 22px ${skin.color}44;">${buttonText}</button>
            </div>
        `;

        const body = dialog.querySelector(".dting-dialog-body");
        body.textContent = String(message || "");

        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        document.body.style.overflow = "hidden";

        const closeBtn = dialog.querySelector(".dting-dialog-close");
        const okBtn = dialog.querySelector(".dting-dialog-btn");

        const cleanup = () => {
            document.removeEventListener("keydown", onKeyDown);
            closeDialog(overlay, options.onClose);
        };

        function onKeyDown(e) {
            if (e.key === "Escape") {
                cleanup();
            }
        }

        document.addEventListener("keydown", onKeyDown);

        closeBtn.addEventListener("click", cleanup);
        okBtn.addEventListener("click", cleanup);

        if (closeOnOverlay) {
            overlay.addEventListener("click", (e) => {
                if (e.target === overlay) {
                    cleanup();
                }
            });
        }

        if (Number.isFinite(options.autoClose) && options.autoClose > 0) {
            window.setTimeout(cleanup, options.autoClose);
        }

        okBtn.focus();
        return { close: cleanup };
    }

    window.DTDialog = {
        show,
        success(message, options) {
            return show("success", message, options);
        },
        error(message, options) {
            return show("error", message, options);
        },
        warning(message, options) {
            return show("warning", message, options);
        }
    };
})();
