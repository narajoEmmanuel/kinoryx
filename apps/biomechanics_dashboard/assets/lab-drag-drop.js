/* KINORYX laboratory, native drag and drop with Dash 2.17+ store updates.
   No external JavaScript dependency and no access to original files here. */
(function () {
  "use strict";
  if (window.__kinoryxWorkspaceEventsInstalled) return;
  window.__kinoryxWorkspaceEventsInstalled = true;

  const allowed = new Set(["0", "1", "2", "3"]);
  const slots = ["left", "right"];
  const fallback = {left: ["0"], right: []};

  function state() {
    const value = window.__kinoryxWorkspaceState;
    const result = {left: [], right: []};
    slots.forEach(function (slot) {
      const items = value && Array.isArray(value[slot]) ? value[slot] : fallback[slot];
      result[slot] = Array.from(new Set(items.map(String).filter(x => allowed.has(x))));
    });
    return result;
  }

  function commit(updated) {
    window.__kinoryxWorkspaceState = updated;
    if (window.dash_clientside && typeof window.dash_clientside.set_props === "function") {
      window.dash_clientside.set_props("lab-workspace-v2", {data: updated});
    }
  }

  function place(channel, slot, fromSlot) {
    channel = String(channel);
    if (!allowed.has(channel) || !slots.includes(slot)) return;
    const updated = state();
    if (fromSlot && slots.includes(fromSlot) && fromSlot !== slot) {
      updated[fromSlot] = updated[fromSlot].filter(x => x !== channel);
    }
    if (!updated[slot].includes(channel)) updated[slot].push(channel);
    commit(updated);
  }

  function remove(channel, slot) {
    if (!slots.includes(slot)) return;
    const updated = state();
    updated[slot] = updated[slot].filter(x => x !== String(channel));
    commit(updated);
  }

  document.addEventListener("dragstart", function (event) {
    const source = event.target.closest(".emg-palette-item, .emg-active-item");
    if (!source || !event.dataTransfer) return;
    const id = source.getAttribute("data-channel");
    if (!allowed.has(id)) return;
    event.dataTransfer.setData("text/plain", JSON.stringify({
      channel: id,
      fromSlot: source.getAttribute("data-from-slot") || null
    }));
    event.dataTransfer.effectAllowed = "move";
    source.classList.add("is-dragging");
  });

  document.addEventListener("dragend", function () {
    document.querySelectorAll(".emg-dropzone").forEach(
      el => el.classList.remove("is-dragover")
    );
    document.querySelectorAll(".is-dragging").forEach(
      el => el.classList.remove("is-dragging")
    );
  });

  document.addEventListener("dragover", function (event) {
    const zone = event.target.closest(".emg-dropzone");
    if (!zone) return;
    event.preventDefault();
    if (event.dataTransfer) event.dataTransfer.dropEffect = "move";
    zone.classList.add("is-dragover");
  });

  document.addEventListener("dragleave", function (event) {
    const zone = event.target.closest(".emg-dropzone");
    if (!zone) return;
    if (!zone.contains(event.relatedTarget)) zone.classList.remove("is-dragover");
  });

  document.addEventListener("drop", function (event) {
    const zone = event.target.closest(".emg-dropzone");
    if (!zone || !event.dataTransfer) return;
    event.preventDefault();
    zone.classList.remove("is-dragover");
    let payload;
    try { payload = JSON.parse(event.dataTransfer.getData("text/plain")); }
    catch (_) { return; }
    if (!payload || !allowed.has(String(payload.channel))) return;
    place(payload.channel, zone.getAttribute("data-slot"), payload.fromSlot);
  });

  document.addEventListener("click", function (event) {
    const add = event.target.closest(".lab-add-button");
    if (add) {
      place(add.getAttribute("data-channel"), add.getAttribute("data-slot"), null);
      return;
    }
    const removeButton = event.target.closest(".emg-remove-item");
    if (removeButton) {
      remove(removeButton.getAttribute("data-channel"), removeButton.getAttribute("data-slot"));
      return;
    }
    if (event.target.closest(".lab-workspace-reset")) {
      commit({left: ["0"], right: []});
    }
  });
})();
