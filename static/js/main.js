document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const openBtn = document.getElementById("openSidebar");
  const closeBtn = document.getElementById("closeSidebar");
  const toggleNav = document.getElementById("toggleNav");
  const desktopNav = window.matchMedia("(min-width: 1024px)");

  const closeSidebar = () => {
    sidebar?.classList.add("-translate-x-full");
    overlay?.classList.add("opacity-0", "pointer-events-none");
    openBtn?.setAttribute("aria-expanded", "false");
  };
  const openSidebar = () => {
    sidebar?.classList.remove("-translate-x-full");
    overlay?.classList.remove("opacity-0", "pointer-events-none");
    openBtn?.setAttribute("aria-expanded", "true");
  };
  const setNavCollapsed = (collapsed, animate = true) => {
    const root = document.documentElement;
    if (animate) root.classList.add("nav-animating");
    root.classList.toggle("nav-collapsed", collapsed);
    document.body.classList.toggle("nav-collapsed", collapsed);
    localStorage.setItem("ls_nav_collapsed", collapsed ? "1" : "0");
    toggleNav?.setAttribute("aria-expanded", collapsed ? "false" : "true");
    if (animate) {
      window.setTimeout(() => root.classList.remove("nav-animating"), 380);
    }
  };
  const syncNavMode = () => {
    if (desktopNav.matches) {
      sidebar?.classList.remove("-translate-x-full");
      overlay?.classList.add("opacity-0", "pointer-events-none");
      setNavCollapsed(localStorage.getItem("ls_nav_collapsed") === "1", false);
    } else {
      document.documentElement.classList.remove("nav-collapsed");
      document.body.classList.remove("nav-collapsed");
    }
  };

  openBtn?.addEventListener("click", openSidebar);
  closeBtn?.addEventListener("click", closeSidebar);
  overlay?.addEventListener("click", closeSidebar);
  toggleNav?.addEventListener("click", () => {
    const collapsed = document.documentElement.classList.contains("nav-collapsed");
    setNavCollapsed(!collapsed, true);
  });
  desktopNav.addEventListener("change", syncNavMode);
  syncNavMode();

  document.querySelectorAll(".alert-banner").forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transition = "opacity 0.3s ease";
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      if (!tabId) return;
      const root = btn.parentElement?.parentElement || document;
      root.querySelectorAll(".tab-btn").forEach((el) => {
        el.classList.remove("active", "bg-sweden-gold", "text-sweden-navy");
        el.classList.add("bg-white/5", "text-white/70");
      });
      btn.classList.add("active", "bg-sweden-gold", "text-sweden-navy");
      btn.classList.remove("bg-white/5", "text-white/70");
      root.querySelectorAll(".tab-pane").forEach((pane) => pane.classList.add("hidden"));
      document.getElementById(tabId)?.classList.remove("hidden");
    });
  });

  document.querySelectorAll("[data-typing]").forEach((card) => {
    const input = card.querySelector("input");
    const button = card.querySelector(".check-typing");
    const result = card.querySelector(".typing-result");
    const check = () => {
      const expected = (input?.dataset.answer || "").trim().toLowerCase();
      const got = (input?.value || "").trim().toLowerCase();
      result.classList.remove("hidden");
      if (got && got === expected) {
        result.textContent = "ถูกต้อง! Bra jobbat!";
        result.className = "typing-result mt-2 text-sm text-emerald-300";
      } else {
        result.textContent = "ยังไม่ถูก ลองพิมพ์ใหม่";
        result.className = "typing-result mt-2 text-sm text-amber-200";
      }
    };
    button?.addEventListener("click", check);
    input?.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        check();
      }
    });
  });

  const matchRoot = document.getElementById("matchGame");
  if (matchRoot) {
    const images = [...matchRoot.querySelectorAll('[data-side="img"]')];
    const choices = [...matchRoot.querySelectorAll('[data-side="sv"]')];
    const total = images.length;
    const status = document.getElementById("matchStatus");
    const checkBtn = document.getElementById("checkMatchBtn");
    let selectedImage = null;
    let checked = false;

    const guessLabel = (card) => card.querySelector(".match-guess");

    const assignedCount = () => images.filter((card) => card.dataset.guess).length;

    const selectCard = (card) => {
      images.forEach((el) => el.classList.remove("selected"));
      selectedImage = card || null;
      if (card) card.classList.add("selected");
    };

    const nextOpenCard = () =>
      images.find((card) => !card.dataset.guess) || selectedImage || images[0] || null;

    const refreshStatus = () => {
      if (checked) return;
      const done = assignedCount();
      if (checkBtn) checkBtn.disabled = done !== total;
      if (status) {
        status.textContent =
          done === total
            ? "เลือกครบแล้ว กดตรวจการจับคู่ได้"
            : `เลือกแล้ว ${done} / ${total} ภาพ — แตะคำด้านล่าง`;
      }
    };

    const clearChoiceUse = (word) => {
      choices.forEach((choice) => {
        if (choice.dataset.match === word) choice.classList.remove("used");
      });
    };

    images.forEach((card) => {
      card.addEventListener("click", () => {
        if (checked) return;
        selectCard(card);
      });
    });

    choices.forEach((choice) => {
      choice.addEventListener("click", () => {
        if (checked) return;
        if (!selectedImage) selectCard(nextOpenCard());
        if (!selectedImage) return;
        const word = choice.dataset.match;
        images.forEach((card) => {
          if (card !== selectedImage && card.dataset.guess === word) {
            delete card.dataset.guess;
            const label = guessLabel(card);
            if (label) label.textContent = "ยังไม่ได้เลือก";
            card.classList.remove("has-guess");
          }
        });
        if (selectedImage.dataset.guess) {
          clearChoiceUse(selectedImage.dataset.guess);
        }
        selectedImage.dataset.guess = word;
        selectedImage.classList.add("has-guess");
        const label = guessLabel(selectedImage);
        if (label) label.textContent = word;
        choices.forEach((el) => el.classList.remove("used"));
        images.forEach((card) => {
          if (card.dataset.guess) {
            choices
              .filter((el) => el.dataset.match === card.dataset.guess)
              .forEach((el) => el.classList.add("used"));
          }
        });
        selectCard(nextOpenCard());
        refreshStatus();
      });
    });

    checkBtn?.addEventListener("click", () => {
      if (assignedCount() !== total || checked) return;
      checked = true;
      checkBtn.disabled = true;
      let correct = 0;
      images.forEach((card) => {
        const ok = card.dataset.guess === card.dataset.match;
        card.classList.remove("selected", "has-guess");
        card.classList.add(ok ? "match-correct" : "match-wrong");
        const label = guessLabel(card);
        if (ok) {
          correct += 1;
          if (label) label.textContent = `ถูกต้อง: ${card.dataset.match}`;
        } else if (label) {
          label.textContent = `ที่เลือก: ${card.dataset.guess || "-"} · เฉลย: ${card.dataset.match}`;
        }
      });
      choices.forEach((choice) => {
        choice.classList.add("locked");
        if (images.some((card) => card.dataset.guess === choice.dataset.match && card.dataset.match === choice.dataset.match)) {
          choice.classList.add("match-correct");
        } else {
          choice.classList.add("match-wrong");
        }
      });
      if (status) {
        status.textContent =
          correct === total
            ? `ถูกทั้งหมด ${correct}/${total} คู่ — Fantastiskt!`
            : `ถูก ${correct}/${total} คู่ — ดูเฉลยใต้ภาพ`;
      }
    });

    selectCard(images[0] || null);
    refreshStatus();
  }

  if (document.body?.dataset.presence === "1") {
    const ping = () => fetch("/presence", { method: "POST", credentials: "same-origin" }).catch(() => {});
    ping();
    setInterval(ping, 15000);
  }

  const liveList = document.getElementById("onlineUsersLive");
  if (liveList && document.body?.dataset.admin === "1") {
    const badge = document.getElementById("onlineCountBadge");
    const esc = (value) =>
      String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    const paint = (payload) => {
      const rows = payload.online || [];
      if (badge) badge.textContent = `${rows.length} คน`;
      if (!rows.length) {
        liveList.innerHTML = '<li class="text-sm text-white/40">ยังไม่มีผู้ใช้ออนไลน์</li>';
      } else {
        liveList.innerHTML = rows
          .map((u) => {
            const roleClass = String(u.role || "") === "Admin" ? "text-sweden-gold" : "text-white/50";
            const latest = (u.earned_achievements || []).slice(-1)[0];
            const medals = latest
              ? `<span class="ach-pill" title="${esc(latest.title_th || "")} · ${esc(latest.title_en || "")}">${latest.icon || "🏅"}</span>`
              : "";
            return `<li class="flex items-center gap-3 rounded-xl border border-white/10 bg-night-200/60 px-3 py-2.5">
              <span class="online-dot"></span>
              <span class="min-w-0 flex-1 font-semibold inline-flex items-center gap-1.5">
                <span class="truncate">${esc(u.display_name || u.username)}</span>
                ${medals ? `<span class="ach-pills">${medals}</span>` : ""}
              </span>
              <span class="text-xs text-white/40">@${esc(u.username)}</span>
              <span class="text-xs ${roleClass}">${esc(u.role || "")}</span>
            </li>`;
          })
          .join("");
      }
      document.querySelectorAll("[data-online-user]").forEach((cell) => {
        const name = cell.getAttribute("data-online-user");
        const on = rows.some((u) => u.username === name);
        cell.innerHTML = on
          ? '<span class="inline-flex items-center gap-1.5 text-emerald-300"><span class="online-dot"></span>ออนไลน์</span>'
          : '<span class="text-white/40">ออฟไลน์</span>';
      });
    };
    const load = () =>
      fetch("/admin/presence", { credentials: "same-origin" })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data && data.ok) paint(data);
        })
        .catch(() => {});
    load();
    setInterval(load, 4000);
  }
});
