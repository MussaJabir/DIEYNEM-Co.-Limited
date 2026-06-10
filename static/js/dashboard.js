// Dashboard Alpine components. Loaded (deferred) before Alpine so the
// `alpine:init` listener is registered before Alpine boots.
document.addEventListener("alpine:init", () => {
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

  // Add-on-demand rows for the project images inline formset: clone the
  // empty-form template, renumber it, append it, and bump TOTAL_FORMS.
  Alpine.data("imageFormset", (initialTotal, prefix) => ({
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
  }));
});
