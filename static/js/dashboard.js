// Dashboard Alpine components. Loaded (deferred) before Alpine so the
// `alpine:init` listener is registered before Alpine boots.
document.addEventListener("alpine:init", () => {
  // Dark-mode toggle. The saved theme is applied pre-paint in the <head>;
  // this just reflects/flips it and persists the choice.
  Alpine.data("themeToggle", () => ({
    dark: document.documentElement.classList.contains("dark"),
    toggle() {
      this.dark = !this.dark;
      document.documentElement.classList.toggle("dark", this.dark);
      try {
        localStorage.setItem("dz-theme", this.dark ? "dark" : "light");
      } catch (e) {
        /* storage unavailable — toggle still works for this session */
      }
    },
  }));

  // Live image preview: show the existing image, then swap to a local
  // preview of a newly-chosen file (no upload needed).
  Alpine.data("imagePreview", (existing = "") => ({
    preview: existing,
    pick(event) {
      const file = event.target.files && event.target.files[0];
      this.preview = file ? URL.createObjectURL(file) : existing;
    },
    clear() {
      this.preview = "";
    },
  }));

  // Add-on-demand rows for an inline formset: clone the empty-form template,
  // renumber it, append it, and bump TOTAL_FORMS. Prefix-driven, so it serves
  // the project images, milestones and updates formsets alike.
  const inlineFormset = (initialTotal, prefix) => ({
    total: initialTotal,
    addRow() {
      const html = this.$refs.emptyRow.innerHTML.replace(
        /__prefix__/g,
        this.total,
      );
      this.$refs.rows.insertAdjacentHTML("beforeend", html);
      this.total += 1;
      const mgmt = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
      if (mgmt) mgmt.value = this.total;
    },
  });
  Alpine.data("inlineFormset", inlineFormset);
  // Backwards-compatible alias kept for the project-images section.
  Alpine.data("imageFormset", inlineFormset);
});
