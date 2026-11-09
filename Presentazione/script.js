(() => {
  "use strict";
  const slides = Array.from(document.querySelectorAll(".slide"));
  const progressBar = document.getElementById("progressBar");
  const counter = document.getElementById("slideCounter");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const dotsContainer = document.getElementById("navDots");
  let current = 0;

  slides.forEach((slide, index) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "nav-dot";
    dot.setAttribute("aria-label", `Vai alla slide ${index + 1}: ${slide.dataset.title || ""}`);
    dot.addEventListener("click", () => goTo(index));
    dotsContainer.appendChild(dot);
  });
  const dots = Array.from(dotsContainer.children);

  function goTo(index) {
    const target = Math.max(0, Math.min(slides.length - 1, index));
    if (target === current) return;
    slides[current].classList.remove("active");
    slides[current].setAttribute("aria-hidden", "true");
    current = target;
    slides[current].classList.add("active");
    slides[current].setAttribute("aria-hidden", "false");
    updateNavigation();
  }

  function updateNavigation() {
    counter.textContent = `${current + 1} / ${slides.length}`;
    progressBar.style.width = `${((current + 1) / slides.length) * 100}%`;
    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === slides.length - 1;
    dots.forEach((dot, index) => {
      dot.classList.toggle("active", index === current);
      dot.setAttribute("aria-current", index === current ? "step" : "false");
    });
    document.title = `${current + 1}/${slides.length} — ${slides[current].dataset.title || "CivicLink"}`;
  }

  prevBtn.addEventListener("click", () => goTo(current - 1));
  nextBtn.addEventListener("click", () => goTo(current + 1));
  document.addEventListener("keydown", event => {
    const key = event.key;
    if (["ArrowRight", " ", "PageDown"].includes(key)) {
      event.preventDefault();
      goTo(current + 1);
    } else if (["ArrowLeft", "PageUp"].includes(key)) {
      event.preventDefault();
      goTo(current - 1);
    } else if (key === "Home") {
      event.preventDefault();
      goTo(0);
    } else if (key === "End") {
      event.preventDefault();
      goTo(slides.length - 1);
    }
  });

  slides.forEach((slide, index) => {
    slide.setAttribute("aria-hidden", index === 0 ? "false" : "true");
  });
  updateNavigation();
})();