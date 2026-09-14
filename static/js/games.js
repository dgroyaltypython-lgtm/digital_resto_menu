(function () {
    "use strict";

    const grid = document.getElementById("gameGrid");
    const chooser = document.getElementById("gameChooser");
    const panel = document.getElementById("gamePanel");
    const back = document.getElementById("backToGames");
    const again = document.getElementById("playAgain");
    const scoreElement = document.getElementById("score");
    const message = document.getElementById("gameMessage");
    const gameName = document.getElementById("gameName");
    const eyebrow = document.getElementById("gameEyebrow");
    const stage = document.getElementById("gameStage");

    let currentGame = null;
    let currentScore = 0;
    let timer = null;
    let raf = null;
    let cleanup = null;

    const GAME_META = {
        memory: ["MEMORY MATCH", "🧠 Coastal Memory"],
        coconut: ["COCONUT TAP", "🥥 Coconut Tap"],
        fish: ["CATCH THE FISH", "🐟 Catch the Fish"],
        reaction: ["QUICK REACTION", "⚡ Quick Reaction"],
        crab: ["WHACK-A-CRAB", "🦀 Whack-a-Crab"],
        shell: ["SHELL SHUFFLE", "🐚 Shell Shuffle"],
        number: ["NUMBER RUSH", "🔢 Number Rush"],
        color: ["COLOR MATCH", "🎨 Color Match"],
        dodge: ["OCEAN DODGE", "🚤 Ocean Dodge"],
        pop: ["BUBBLE POP", "🫧 Bubble Pop"]
    };

    function setScore(value) {
        currentScore = value;
        scoreElement.textContent = String(value);
    }

    function setMessage(text) {
        message.textContent = text;
    }

    function stopGame() {
        if (timer) { clearInterval(timer); timer = null; }
        if (raf) { cancelAnimationFrame(raf); raf = null; }
        if (typeof cleanup === "function") { cleanup(); cleanup = null; }
        stage.innerHTML = "";
    }

    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function openGame(name) {
        if (!GAME_META[name]) return;
        stopGame();
        currentGame = name;
        setScore(0);
        setMessage("");
        chooser.classList.add("d-none");
        grid.classList.add("d-none");
        panel.classList.remove("d-none");

        eyebrow.textContent = GAME_META[name][0];
        gameName.textContent = GAME_META[name][1];

        const runners = {
            memory: startMemory,
            coconut: () => startTap("coconut"),
            fish: () => startTap("fish"),
            reaction: startReaction,
            crab: startCrab,
            shell: startShell,
            number: startNumber,
            color: startColor,
            dodge: startDodge,
            pop: startPop
        };
        runners[name]();
    }

    grid.querySelectorAll(".game-card").forEach(card => {
        card.addEventListener("click", () => openGame(card.dataset.game));
    });

    back.addEventListener("click", () => {
        stopGame();
        panel.classList.add("d-none");
        chooser.classList.remove("d-none");
        grid.classList.remove("d-none");
    });

    again.addEventListener("click", () => {
        if (currentGame) openGame(currentGame);
    });

    function startMemory() {
        stage.innerHTML = '<div class="play-area"><p class="instruction">Match all 8 pairs.</p><div class="memory-grid"></div></div>';
        const memoryGrid = stage.querySelector(".memory-grid");
        const symbols = ["🐟","🐟","🦀","🦀","🥥","🥥","🌴","🌴","🍤","🍤","🐚","🐚","🌊","🌊","🏝️","🏝️"];
        symbols.sort(() => Math.random() - 0.5);
        let first = null, locked = false, matches = 0;

        symbols.forEach(symbol => {
            const card = document.createElement("button");
            card.type = "button";
            card.className = "memory-card";
            card.dataset.symbol = symbol;
            card.textContent = "❔";
            card.addEventListener("click", () => {
                if (locked || card.classList.contains("matched") || card === first) return;
                card.classList.add("flipped");
                card.textContent = symbol;
                if (!first) { first = card; return; }

                locked = true;
                const second = card;
                if (first.dataset.symbol === second.dataset.symbol) {
                    first.classList.add("matched");
                    second.classList.add("matched");
                    matches++;
                    setScore(matches * 10);
                    first = null;
                    locked = false;
                    if (matches === 8) setMessage("🎉 Perfect! Every coastal pair matched!");
                } else {
                    const oldFirst = first;
                    setTimeout(() => {
                        oldFirst.classList.remove("flipped");
                        second.classList.remove("flipped");
                        oldFirst.textContent = "❔";
                        second.textContent = "❔";
                        first = null;
                        locked = false;
                    }, 650);
                }
            });
            memoryGrid.appendChild(card);
        });
    }

    function startTap(type) {
        const emoji = type === "coconut" ? "🥥" : "🐟";
        const secondsTotal = type === "coconut" ? 15 : 20;
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Tap the target as many times as you can.</p>' +
            '<div class="tap-arena"><button type="button" class="target" id="tapTarget" aria-label="Tap target">' + emoji + '</button></div>' +
            '<div class="timer">TIME <b id="tapTime">' + secondsTotal + '</b>s</div></div>';

        const arena = stage.querySelector(".tap-arena");
        const target = stage.querySelector("#tapTarget");
        const timeEl = stage.querySelector("#tapTime");
        let seconds = secondsTotal;

        function move() {
            const x = randomInt(5, Math.max(5, arena.clientWidth - 73));
            const y = randomInt(5, Math.max(5, arena.clientHeight - 73));
            target.style.left = x + "px";
            target.style.top = y + "px";
        }
        target.addEventListener("click", () => { setScore(currentScore + 1); move(); });
        move();

        timer = setInterval(() => {
            seconds--;
            timeEl.textContent = String(Math.max(0, seconds));
            if (seconds <= 0) {
                clearInterval(timer); timer = null;
                setMessage(emoji + " Time! Your score: " + currentScore);
            }
        }, 1000);
    }

    function startReaction() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Tap when the circle turns green. Early taps lose the round.</p>' +
            '<button type="button" id="reactionButton" class="reaction-button">WAIT...</button>' +
            '<div class="timer">REACTION <b id="reactionTime">—</b> ms</div></div>';
        const btn = stage.querySelector("#reactionButton");
        const timeEl = stage.querySelector("#reactionTime");
        let ready = false, startedAt = 0, delayTimer = null;

        function arm() {
            ready = false;
            btn.className = "reaction-button";
            btn.textContent = "WAIT...";
            delayTimer = setTimeout(() => {
                ready = true;
                startedAt = performance.now();
                btn.classList.add("go");
                btn.textContent = "TAP!";
            }, randomInt(1200, 3000));
        }

        btn.addEventListener("click", () => {
            if (!ready) {
                clearTimeout(delayTimer);
                btn.classList.add("early");
                btn.textContent = "TOO EARLY";
                setMessage("Try again — wait for green.");
                setTimeout(arm, 900);
                return;
            }
            const ms = Math.round(performance.now() - startedAt);
            timeEl.textContent = String(ms);
            setScore(Math.max(1, 1000 - ms));
            setMessage(ms < 300 ? "⚡ Lightning fast!" : ms < 500 ? "🔥 Great reaction!" : "Nice! Try to beat it.");
            ready = false;
            setTimeout(arm, 1100);
        });
        arm();
        cleanup = () => clearTimeout(delayTimer);
    }

    function startCrab() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Catch the crab. A new one appears every moment.</p>' +
            '<div class="crab-grid"></div></div>';
        const gridEl = stage.querySelector(".crab-grid");
        const holes = [];
        for (let i = 0; i < 9; i++) {
            const b = document.createElement("button");
            b.type = "button"; b.className = "crab-hole"; b.textContent = "🌊";
            b.addEventListener("click", () => {
                if (b.textContent === "🦀") {
                    setScore(currentScore + 1);
                    b.textContent = "🌊";
                }
            });
            holes.push(b); gridEl.appendChild(b);
        }
        function place() {
            holes.forEach(h => { if (h.textContent === "🦀") h.textContent = "🌊"; });
            holes[randomInt(0, holes.length - 1)].textContent = "🦀";
        }
        place();
        timer = setInterval(place, 850);
        cleanup = () => holes.forEach(h => h.textContent = "🌊");
    }

    function startShell() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">One shell hides the pearl. Find it.</p><div class="shell-grid"></div></div>';
        const sg = stage.querySelector(".shell-grid");
        let found = false;
        function round() {
            found = false; sg.innerHTML = "";
            const pearl = randomInt(0, 2);
            for (let i = 0; i < 3; i++) {
                const b = document.createElement("button");
                b.type = "button"; b.className = "shell"; b.textContent = "🐚";
                b.addEventListener("click", () => {
                    if (found) return;
                    if (i === pearl) {
                        found = true; b.textContent = "🦪"; setScore(currentScore + 10);
                        setMessage("✨ You found the pearl!");
                    } else {
                        b.textContent = "❌"; setScore(Math.max(0, currentScore - 2));
                        setMessage("Not this shell — try again.");
                    }
                });
                sg.appendChild(b);
            }
        }
        round();
    }

    function startNumber() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Tap numbers from 1 to 12 in order.</p><div class="number-grid"></div></div>';
        const ng = stage.querySelector(".number-grid");
        let next = 1;
        function round() {
            ng.innerHTML = "";
            const nums = Array.from({length: 12}, (_, i) => i + 1).sort(() => Math.random() - 0.5);
            next = 1; setScore(0);
            nums.forEach(n => {
                const b = document.createElement("button");
                b.type = "button"; b.className = "number-button"; b.textContent = n;
                b.addEventListener("click", () => {
                    if (n !== next) { setMessage("❌ Start with " + next + "."); return; }
                    b.disabled = true; setScore(currentScore + 1); next++;
                    if (next === 13) setMessage("🏆 Number Rush complete!");
                });
                ng.appendChild(b);
            });
        }
        round();
    }

    function startColor() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Tap the button matching the target color.</p>' +
            '<div id="colorTarget" class="color-target"></div><div class="color-grid"></div></div>';
        const colors = [
            ["Aqua","#22d3ee"], ["Teal","#2dd4bf"], ["Purple","#a855f7"], ["Gold","#f6d365"]
        ];
        const targetEl = stage.querySelector("#colorTarget"), cg = stage.querySelector(".color-grid");
        let target;
        function round() {
            target = colors[randomInt(0, colors.length - 1)];
            targetEl.textContent = "TARGET: " + target[0];
            cg.innerHTML = "";
            colors.slice().sort(() => Math.random() - 0.5).forEach(c => {
                const b = document.createElement("button");
                b.type = "button"; b.className = "color-button"; b.textContent = c[0];
                b.style.background = c[1];
                b.addEventListener("click", () => {
                    if (c[0] === target[0]) {
                        setScore(currentScore + 10); setMessage("✅ Correct!"); round();
                    } else {
                        setScore(Math.max(0, currentScore - 3)); setMessage("Try again.");
                    }
                });
                cg.appendChild(b);
            });
        }
        round();
    }

    function startDodge() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Move the boat left and right. Avoid the rocks.</p>' +
            '<div class="dodge-arena" id="dodgeArena"><div class="dodge-boat" id="dodgeBoat">🚤</div><div class="dodge-obstacle" id="dodgeObstacle">🌊</div></div>' +
            '<div class="dodge-controls"><button type="button" class="dodge-control" id="left">←</button><button type="button" class="dodge-control" id="right">→</button></div></div>';
        const arena = stage.querySelector("#dodgeArena"), boat = stage.querySelector("#dodgeBoat"), obstacle = stage.querySelector("#dodgeObstacle");
        let x = arena.clientWidth / 2 - 20, y = -50, alive = true, last = performance.now(), velocity = 0;
        function move(dir) { velocity = dir * 7; }
        const left = stage.querySelector("#left"), right = stage.querySelector("#right");
        left.onpointerdown = () => move(-1); right.onpointerdown = () => move(1);
        left.onpointerup = right.onpointerup = () => velocity = 0;
        let keys = {};
        function keydown(e){ keys[e.key]=true; }
        function keyup(e){ keys[e.key]=false; }
        window.addEventListener("keydown",keydown); window.addEventListener("keyup",keyup);
        function frame(now) {
            if (!alive) return;
            const dt = Math.min(40, now-last); last=now;
            if (keys.ArrowLeft) x -= 7 * dt/16.7;
            if (keys.ArrowRight) x += 7 * dt/16.7;
            x += velocity * dt/16.7;
            x = Math.max(4, Math.min(arena.clientWidth - 50, x));
            y += 4.3 * dt/16.7;
            if (y > arena.clientHeight + 50) {
                y = -55; x = randomInt(5, Math.max(5, arena.clientWidth-45)); setScore(currentScore+1);
            }
            boat.style.left = x + "px"; boat.style.transform = "none";
            obstacle.style.left = randomInt(5, Math.max(5, arena.clientWidth-40)) + "px";
            obstacle.style.top = y + "px";
            const br=boat.getBoundingClientRect(), or=obstacle.getBoundingClientRect();
            if (br.left<or.right && br.right>or.left && br.top<or.bottom && br.bottom>or.top) {
                alive=false; setMessage("🌊 Wave hit! Score: "+currentScore);
                return;
            }
            raf=requestAnimationFrame(frame);
        }
        raf=requestAnimationFrame(frame);
        cleanup=()=>{alive=false; window.removeEventListener("keydown",keydown);window.removeEventListener("keyup",keyup);};
    }

    function startPop() {
        stage.innerHTML =
            '<div class="play-area"><p class="instruction">Pop as many bubbles as possible before time runs out.</p>' +
            '<div class="bubble-arena" id="bubbleArena"></div><div class="timer">TIME <b id="bubbleTime">20</b>s</div></div>';
        const arena=stage.querySelector("#bubbleArena"), timeEl=stage.querySelector("#bubbleTime");
        let seconds=20;
        function addBubble() {
            const b=document.createElement("button");
            b.type="button"; b.className="bubble";
            const size=randomInt(35,75); b.style.width=size+"px";b.style.height=size+"px";
            b.textContent=["🫧","💧","✨"][randomInt(0,2)];
            b.style.left=randomInt(2,Math.max(2,arena.clientWidth-size-2))+"px";
            b.style.top=randomInt(2,Math.max(2,arena.clientHeight-size-2))+"px";
            b.addEventListener("click",()=>{b.remove();setScore(currentScore+1);});
            arena.appendChild(b);
            setTimeout(()=>b.remove(),3500);
        }
        for(let i=0;i<7;i++) addBubble();
        const spawn=setInterval(addBubble,700);
        timer=setInterval(()=>{
            seconds--;timeEl.textContent=String(seconds);
            if(seconds<=0){
                clearInterval(timer);timer=null;clearInterval(spawn);
                setMessage("🫧 Time! You popped "+currentScore+" bubbles.");
            }
        },1000);
        cleanup=()=>clearInterval(spawn);
    }
})();