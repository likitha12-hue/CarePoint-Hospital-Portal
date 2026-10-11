document.addEventListener("DOMContentLoaded", () => {

  /* ============ 1. Doctor list: filter + search + details modal ============ */
  const grid = document.getElementById("doctor-grid");
  if (grid) {
    const cards = grid.querySelectorAll(".doctor-card");
    const buttons = document.querySelectorAll("#dept-buttons .dept-btn");
    const search = document.getElementById("doctor-search");
    const noResults = document.getElementById("no-results");
    let activeDept = "all";

    const applyFilters = () => {
      const text = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(card => {
        const show = (activeDept === "all" || card.dataset.dept === activeDept) &&
                     (!text || card.dataset.text.includes(text));
        card.classList.toggle("d-none", !show);
        if (show) visible++;
      });
      noResults.classList.toggle("d-none", visible !== 0 || cards.length === 0);
    };

    buttons.forEach(btn => btn.addEventListener("click", () => {
      activeDept = btn.dataset.dept;
      buttons.forEach(b => b.classList.toggle("active", b === btn));
      applyFilters();
    }));
    search.addEventListener("input", applyFilters);
    applyFilters();

    document.querySelectorAll(".details-btn").forEach(btn => btn.addEventListener("click", () => {
      document.getElementById("modal-name").textContent = btn.dataset.name;
      document.getElementById("modal-dept").textContent = btn.dataset.dept;
      document.getElementById("modal-spec").textContent = btn.dataset.spec;
      document.getElementById("modal-fee").textContent = btn.dataset.fee;
      document.getElementById("modal-days").textContent = btn.dataset.days;
    }));
  }

  /* ============ 2. Booking page: doctor picker + slots + summary ============ */
  const slotGrid = document.getElementById("slot-grid");
  if (slotGrid) {
    const radios = document.querySelectorAll(".doctor-radio");
    const dateInput = document.getElementById("id_date");
    const hidden = document.getElementById("id_time_slot");
    const hint = document.getElementById("day-hint");
    const sum = {
      doctor: document.getElementById("sum-doctor"), date: document.getElementById("sum-date"),
      time: document.getElementById("sum-time"), fee: document.getElementById("sum-fee"),
    };
    let keepSlot = hidden.value;   // survives a failed form submit

    dateInput.min = new Date().toISOString().split("T")[0];
    const selectedDoctor = () => document.querySelector(".doctor-radio:checked");

    // department chips filter the doctor cards
    document.querySelectorAll("#booking-form .dept-btn").forEach(btn => btn.addEventListener("click", () => {
      document.querySelectorAll("#booking-form .dept-btn").forEach(b => b.classList.toggle("active", b === btn));
      document.querySelectorAll(".pick-item").forEach(item =>
        item.classList.toggle("d-none", btn.dataset.dept !== "all" && item.dataset.dept !== btn.dataset.dept));
    }));

    function updateSummary() {
      const d = selectedDoctor();
      sum.doctor.textContent = d ? d.dataset.label : "—";
      sum.fee.textContent = d ? "₹" + d.dataset.fee : "—";
      sum.date.textContent = dateInput.value
        ? new Date(dateInput.value + "T00:00").toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short", year: "numeric" })
        : "—";
      sum.time.textContent = hidden.value || "—";
    }

    function message(html) { slotGrid.innerHTML = `<div class="msg">${html}</div>`; }

    async function loadSlots() {
      const d = selectedDoctor();
      hint.textContent = "";
      if (!d || !dateInput.value) {
        hidden.value = "";
        message('<span class="text-muted">Choose a doctor and a date to see available slots.</span>');
        return updateSummary();
      }
      message('<span class="text-muted"><span class="spinner-border spinner-border-sm"></span> Loading slots…</span>');
      try {
        const res = await fetch(`${slotGrid.dataset.url}?doctor=${d.value}&date=${dateInput.value}`);
        if (!res.ok) throw new Error("bad response");
        const data = await res.json();
        slotGrid.innerHTML = "";
        if (!data.works_that_day) {
          hidden.value = "";
          message('<span class="text-danger"><i class="bi bi-calendar-x"></i> This doctor is not available on the selected day. Please pick another date.</span>');
          return updateSummary();
        }
        data.slots.forEach(s => {
          const b = document.createElement("button");
          b.type = "button";
          b.className = "slot-btn";
          b.textContent = s.time;
          b.disabled = s.booked;
          if (!s.booked && s.time === keepSlot) { b.classList.add("selected"); hidden.value = s.time; }
          b.addEventListener("click", () => {
            slotGrid.querySelectorAll(".slot-btn").forEach(x => x.classList.remove("selected"));
            b.classList.add("selected");
            hidden.value = s.time;
            keepSlot = s.time;
            updateSummary();
          });
          slotGrid.appendChild(b);
        });
        if (!slotGrid.querySelector(".selected")) hidden.value = "";
      } catch (e) {
        message('<span class="text-danger">Could not load slots. Please refresh and try again.</span>');
      }
      updateSummary();
    }

    radios.forEach(r => r.addEventListener("change", () => { keepSlot = ""; loadSlots(); }));
    dateInput.addEventListener("change", () => { keepSlot = ""; loadSlots(); });

    // block submit if no slot picked (server still validates everything)
    document.getElementById("booking-form").addEventListener("submit", e => {
      if (!hidden.value) {
        e.preventDefault();
        slotGrid.scrollIntoView({ behavior: "smooth", block: "center" });
        message('<span class="text-danger">Please select a time slot first.</span>');
      }
    });

    loadSlots();
  }

  /* ============ 3. Dashboard: cancel confirmation modal ============ */
  document.querySelectorAll(".cancel-btn").forEach(btn => btn.addEventListener("click", () => {
    document.getElementById("cancel-form").action = btn.dataset.action;
  }));
});
