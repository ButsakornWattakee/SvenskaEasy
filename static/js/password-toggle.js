document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const wrap = button.closest("[data-password-field]");
      const input = wrap ? wrap.querySelector("input") : null;
      if (!input) return;
      const hidden = input.type === "password";
      input.type = hidden ? "text" : "password";
      button.setAttribute("aria-label", hidden ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน");
      button.setAttribute("title", hidden ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน");
      button.querySelector(".icon-eye")?.classList.toggle("hidden", hidden);
      button.querySelector(".icon-eye-off")?.classList.toggle("hidden", !hidden);
    });
  });
});
