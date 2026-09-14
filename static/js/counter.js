/*
 * Coastal Pearl - Live Counter Dashboard
 * Custom bell for every new service request.
 * Polls the server every 2 seconds.
 */

let enabled = false;
let lastCallIds = new Set();
let overlayId = null;
let firstLoad = true;
let ringing = false;


/* =========================================================
   HELPERS
   ========================================================= */

function cookie(name) {
    const match = document.cookie.match(
        new RegExp("(^|; )" + name + "=([^;]*)")
    );

    return match ? decodeURIComponent(match[2]) : "";
}


function escapeHtml(value) {
    return String(value).replace(
        /[&<>"']/g,
        function (character) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[character];
        }
    );
}


/* =========================================================
   CUSTOM RINGER
   ========================================================= */

function getBell() {
    return document.getElementById("serviceBell");
}


async function playCustomBell() {
    if (!enabled || ringing) {
        return;
    }

    const bell = getBell();

    if (!bell) {
        console.error(
            "Custom service bell audio element not found."
        );
        return;
    }

    ringing = true;

    const repeatElement = document.getElementById(
        "repeatControl"
    );

    const repeatCount = repeatElement
        ? Math.max(1, Number(repeatElement.value) || 3)
        : 3;

    try {
        for (let i = 0; i < repeatCount; i++) {
            bell.currentTime = 0;
            await bell.play();

            await new Promise(function (resolve) {
                const finished = function () {
                    bell.removeEventListener("ended", finished);
                    resolve();
                };

                bell.addEventListener("ended", finished);
            });

            if (i < repeatCount - 1) {
                await new Promise(function (resolve) {
                    setTimeout(resolve, 250);
                });
            }
        }
    } catch (error) {
        console.error(
            "Custom bell playback failed:",
            error
        );
    } finally {
        ringing = false;
    }
}

window.playRestaurantBell = playCustomBell;


/* =========================================================
   ENABLE RINGER
   ========================================================= */

const enableButton = document.getElementById("enable");

if (enableButton) {
    enableButton.onclick = async function () {
        const bell = getBell();

        if (!bell) {
            alert("Custom service bell file was not found.");
            return;
        }

        try {
            bell.currentTime = 0;
            await bell.play();
            bell.pause();
            bell.currentTime = 0;

            enabled = true;

            enableButton.textContent = "🔊 RINGER ENABLED";
            enableButton.classList.add("active");

            const system = document.getElementById("sys");

            if (system) {
                system.textContent = "RINGER ON";
            }

            const status = document.getElementById("ringerStatus");

            if (status) {
                status.textContent = "● RINGER ON";
                status.classList.remove("off");
                status.classList.add("on");
            }
        } catch (error) {
            console.error(
                "Unable to enable custom ringer:",
                error
            );

            alert(
                "The browser blocked the sound. " +
                "Please click ENABLE RINGER again."
            );
        }
    };
}


/* =========================================================
   TEST RINGER
   ========================================================= */

const testButton = document.getElementById("test");

if (testButton) {
    testButton.onclick = async function () {
        if (!enabled) {
            alert("Please click ENABLE RINGER first.");
            return;
        }

        await playCustomBell();
    };
}


/* =========================================================
   CSRF
   ========================================================= */

function getCsrfToken() {
    return cookie("csrftoken");
}


/* =========================================================
   RENDER CALLS
   ========================================================= */

function render(calls) {
    const pendingElement = document.getElementById("pending");
    const acknowledgedElement = document.getElementById("ack");

    if (pendingElement) {
        pendingElement.textContent = calls.filter(
            function (call) {
                return call.status === "pending";
            }
        ).length;
    }

    if (acknowledgedElement) {
        acknowledgedElement.textContent = calls.filter(
            function (call) {
                return call.status === "acknowledged";
            }
        ).length;
    }

    const box = document.getElementById("calls");

    if (!box) {
        return;
    }

    if (!calls.length) {
        box.innerHTML = `
            <div class="empty">
                <div class="empty-icon">🪼</div>
                <strong>All quiet for now</strong>
                <span>New calls appear automatically.</span>
            </div>
        `;
        return;
    }

    box.innerHTML = calls.map(
        function (call) {
            const acknowledged = call.status === "acknowledged";

            return `
                <article class="glass call ${acknowledged ? "ack" : ""}">
                    <div class="call-head">
                        <div>
                            <div class="eyebrow">TABLE</div>
                            <div class="call-table">
                                ${escapeHtml(call.table_number)}
                            </div>
                        </div>

                        <div class="call-type">
                            ${escapeHtml(call.request_type)}
                        </div>
                    </div>

                    <div class="call-time">
                        ${escapeHtml(call.created_at)}
                    </div>

                    <div class="call-actions">
                        ${
                            !acknowledged
                                ? `
                                    <button
                                        onclick="updateCallStatus(
                                            ${call.id},
                                            'acknowledged'
                                        )"
                                    >
                                        ✓ ACKNOWLEDGE
                                    </button>
                                `
                                : `
                                    <button
                                        onclick="updateCallStatus(
                                            ${call.id},
                                            'completed'
                                        )"
                                    >
                                        ✓ COMPLETE
                                    </button>
                                `
                        }

                        <button
                            class="done"
                            onclick="updateCallStatus(
                                ${call.id},
                                'completed'
                            )"
                        >
                            DONE
                        </button>
                    </div>
                </article>
            `;
        }
    ).join("");
}


/* =========================================================
   UPDATE CALL STATUS
   ========================================================= */

async function updateCallStatus(id, newStatus) {
    try {
        const response = await fetch(
            `/api/service-call/${id}/status/`,
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        if (
            response.status === 401 ||
            response.status === 403
        ) {
            window.location.href = "/counter/";
            return;
        }

        if (!response.ok) {
            console.error("Unable to update service call.");
            return;
        }

        if (
            newStatus === "acknowledged" ||
            newStatus === "completed"
        ) {
            const overlay = document.getElementById("overlay");

            if (overlay) {
                overlay.classList.remove("show");
            }

            overlayId = null;
        }

        await loadCalls();
    } catch (error) {
        console.error("Status update error:", error);
    }
}

window.updateCallStatus = updateCallStatus;


/* =========================================================
   SHOW NEW CALL
   ========================================================= */

function showNewCall(call) {
    const table = document.getElementById("otable");
    const type = document.getElementById("otype");
    const overlay = document.getElementById("overlay");
    const last = document.getElementById("last");

    if (table) {
        table.textContent = call.table_number;
    }

    if (type) {
        type.textContent = String(
            call.request_type || "SERVICE"
        ).toUpperCase();
    }

    if (last) {
        last.textContent = call.table_number;
    }

    if (overlay) {
        overlayId = call.id;
        overlay.classList.add("show");
    }

    /*
     * Every request type triggers the custom bell:
     * Service, Water, Bill, Assistance, etc.
     */
    playCustomBell();
}


/* =========================================================
   LOAD SERVICE CALLS
   ========================================================= */

async function loadCalls() {
    try {
        const response = await fetch(
            window.API.calls,
            {
                credentials: "same-origin",
                cache: "no-store"
            }
        );

        if (
            response.status === 401 ||
            response.status === 403
        ) {
            window.location.href = "/counter/";
            return;
        }

        if (!response.ok) {
            throw new Error(
                "HTTP " + response.status
            );
        }

        const data = await response.json();
        const calls = data.calls || [];

        const currentIds = new Set(
            calls.map(
                function (call) {
                    return call.id;
                }
            )
        );

        /*
         * Only genuinely new pending calls ring.
         * Request type does not matter.
         */
        if (!firstLoad) {
            const newCalls = calls.filter(
                function (call) {
                    return (
                        call.status === "pending" &&
                        !lastCallIds.has(call.id)
                    );
                }
            );

            if (newCalls.length) {
                showNewCall(newCalls[0]);
            }
        }

        /*
         * Existing calls do not ring when the dashboard
         * is opened or refreshed.
         */
        firstLoad = false;
        lastCallIds = currentIds;

        render(calls);

        const live = document.getElementById("live");

        if (live) {
            live.textContent = "● LIVE";
            live.classList.remove("offline");
        }
    } catch (error) {
        console.error(
            "Service call polling error:",
            error
        );

        const live = document.getElementById("live");

        if (live) {
            live.textContent = "● RECONNECTING";
            live.classList.add("offline");
        }
    }
}


/* =========================================================
   OVERLAY ACKNOWLEDGE
   ========================================================= */

const acknowledgeButton = document.getElementById("oack");

if (acknowledgeButton) {
    acknowledgeButton.onclick = function () {
        if (overlayId !== null) {
            updateCallStatus(
                overlayId,
                "acknowledged"
            );
        } else {
            const overlay = document.getElementById("overlay");

            if (overlay) {
                overlay.classList.remove("show");
            }
        }
    };
}


/* =========================================================
   INITIAL LOAD
   ========================================================= */

loadCalls();


/* =========================================================
   LIVE POLLING
   ========================================================= */

/*
 * Counter checks for new calls every 2 seconds.
 */
setInterval(loadCalls, 2000);
