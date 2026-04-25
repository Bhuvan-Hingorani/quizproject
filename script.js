// ─── TIMER ───────────────────────────────────────────────────────────────────
const timerEl    = document.getElementById("timer");
const progressEl = document.getElementById("timerProgress");
const totalTime  = parseInt(document.body.dataset.time) || 1800;
let   timeLeft   = totalTime;

function updateTimer() {
  const m = Math.floor(timeLeft / 60);
  const s = timeLeft % 60;
  timerEl.textContent = m + ":" + (s < 10 ? "0" : "") + s;

  if (progressEl) progressEl.style.width = (timeLeft / totalTime * 100) + "%";
  if (timeLeft <= 120) timerEl.closest(".timer-display").classList.add("danger");

  timeLeft--;
  if (timeLeft < 0) {
    clearInterval(countdown);
    alert("⏰ Time's up! Submitting your quiz.");
    document.getElementById("quizForm").submit();
  }
}

updateTimer();
const countdown = setInterval(updateTimer, 1000);

// ─── QUESTION NAVIGATION ─────────────────────────────────────────────────────
const cards    = document.querySelectorAll(".question-card");
const dots     = document.querySelectorAll(".q-dot");
const prevBtn  = document.getElementById("prevBtn");
const nextBtn  = document.getElementById("nextBtn");
const submitBtn= document.getElementById("submitBtn");
const qCurrent = document.getElementById("qCurrent");

let current = 0;
const total = cards.length;

function showQuestion(idx) {
  cards.forEach((c, i) => {
    c.style.display = i === idx ? "block" : "none";
  });
  dots.forEach((d, i) => {
    d.classList.toggle("active", i === idx);
  });
  if (qCurrent) qCurrent.textContent = idx + 1;

  prevBtn.disabled = idx === 0;
  nextBtn.style.display   = idx === total - 1 ? "none"         : "inline-block";
  submitBtn.style.display = idx === total - 1 ? "inline-block" : "none";
}

prevBtn.addEventListener("click", () => { if (current > 0)       { current--; showQuestion(current); } });
nextBtn.addEventListener("click", () => { if (current < total-1) { current++; showQuestion(current); } });

dots.forEach((dot, i) => dot.addEventListener("click", () => { current = i; showQuestion(i); }));

// Mark dot answered + highlight selected option
document.querySelectorAll("input[type='radio']").forEach(radio => {
  radio.addEventListener("change", () => {
    const card = radio.closest(".question-card");
    const idx  = Array.from(cards).indexOf(card);
    if (idx >= 0 && dots[idx]) dots[idx].classList.add("answered");

    card.querySelectorAll(".option").forEach(o => o.classList.remove("selected"));
    radio.closest(".option").classList.add("selected");
  });
});

// Restore already-checked on back (browser cache)
document.querySelectorAll("input[type='radio']:checked").forEach(radio => {
  const card = radio.closest(".question-card");
  const idx  = Array.from(cards).indexOf(card);
  if (idx >= 0 && dots[idx]) dots[idx].classList.add("answered");
  if (radio.closest(".option")) radio.closest(".option").classList.add("selected");
});

showQuestion(0);
