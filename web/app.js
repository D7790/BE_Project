"use strict";
const $ = id => document.getElementById(id);
let latestSnapshot = null;
let controlBusy = false;
let toastTimer;
const fmt = (value, digits = 1) => Number.isFinite(value) ? value.toFixed(digits) : "—";
const text = (id, value) => { $(id).textContent = value; };
function duration(hours) {
  if (!Number.isFinite(hours)) return "—";
  const minutes = Math.max(0, Math.round(hours * 60));
  return minutes < 60 ? minutes + " min" : Math.floor(minutes / 60) + " h " + minutes % 60 + " min";
}
function toast(message) {
  text("toast", message);
  $("toast").hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $("toast").hidden = true; }, 6000);
}
function controls(enabled) {
  $("runtimeSlider").disabled = !enabled || controlBusy;
  for (const button of document.querySelectorAll(".load-actions button, .scenario")) {
    button.disabled = !enabled || controlBusy;
  }
}
async function command(action, value) {
  if (controlBusy || !latestSnapshot?.controls_enabled || latestSnapshot.stale) return;
  controlBusy = true;
  controls(false);
  try {
    const response = await fetch("/api/control", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({action, value}), signal: AbortSignal.timeout(4000)
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "Command failed.");
    toast(body.message);
    if (action === "scenario") {
      for (const button of document.querySelectorAll(".scenario")) {
        const selected = button.dataset.scenario === value;
        button.classList.toggle("selected", selected);
        button.setAttribute("aria-pressed", String(selected));
      }
    }
  } catch (error) {
    toast(error.message);
  } finally {
    controlBusy = false;
    await poll();
  }
}
function renderEvents(events) {
  const list = $("eventList");
  list.replaceChildren();
  for (const event of events.slice(0, 7)) {
    const li = document.createElement("li");
    const time = document.createElement("time");
    time.dateTime = event.at;
    time.textContent = new Date(event.at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", second: "2-digit"});
    const content = document.createElement("div");
    const title = document.createElement("strong");
    const detail = document.createElement("p");
    title.textContent = event.title;
    detail.textContent = event.detail;
    content.append(title, detail);
    li.append(time, content);
    list.append(li);
  }
}
function renderChart(history) {
  const svg = $("powerChart");
  const width = svg.parentElement.clientWidth;
  const height = svg.parentElement.clientHeight;
  if (!width || !height) return;
  svg.setAttribute("viewBox", "0 0 " + width + " " + height);
  const left = 36, right = width - 12, top = 12, bottom = height - 29;
  const values = history.filter(row => row.sensor_ok).flatMap(row => [row.battery_w, row.load_w]).filter(Number.isFinite);
  const low = Math.min(0, ...values);
  const high = Math.max(1, ...values);
  const padding = Math.max(1, (high - low) * 0.12);
  const ymin = low < 0 ? low - padding : 0, ymax = high + padding;
  const y = v => bottom - (v - ymin) / (ymax - ymin) * (bottom - top);
  const start = history.length ? Date.parse(history[0].received_at) : Date.now();
  const end = history.length > 1 ? Date.parse(history.at(-1).received_at) : start + 1000;
  const x = value => left + (value - start) / Math.max(1000, end - start) * (right - left);
  let markup = "<title>Battery and total load power, watts. Gaps indicate missing measurements.</title>";
  for (let i = 0; i <= 3; i++) {
    const value = ymin + (ymax - ymin) * i / 3;
    markup += '<line class="chart-grid" x1="' + left + '" x2="' + right + '" y1="' + y(value) + '" y2="' + y(value) + '"/>';
    markup += '<text class="chart-label" text-anchor="end" x="' + (left - 9) + '" y="' + (y(value) + 3) + '">' + value.toFixed(0) + "</text>";
  }
  markup += '<text class="chart-label" x="2" y="9">W</text>';
  const ticks = width < 400 ? 3 : 4;
  for (let i = 0; i < ticks; i++) {
    const stamp = start + (end - start) * i / (ticks - 1);
    const label = new Date(stamp).toLocaleTimeString([], {minute: "2-digit", second: "2-digit"});
    markup += '<text class="chart-label" text-anchor="' + (i === 0 ? "start" : i === ticks - 1 ? "end" : "middle") +
      '" x="' + x(stamp) + '" y="' + (height - 6) + '">' + label + "</text>";
  }
  for (const [key, cls] of [["load_w", "chart-line-load"], ["battery_w", "chart-line-battery"]]) {
    let path = "", pen = false, previous = null;
    for (const row of history) {
      const stamp = Date.parse(row.received_at);
      if (!row.sensor_ok || !Number.isFinite(row[key])) { pen = false; continue; }
      if (previous !== null && stamp - previous > 3000) pen = false;
      path += (pen ? " L " : " M ") + x(stamp).toFixed(2) + " " + y(row[key]).toFixed(2);
      pen = true;
      previous = stamp;
    }
    markup += '<path class="' + cls + '" d="' + path + '"/>';
  }
  svg.innerHTML = markup;
  $("chartEmpty").hidden = values.length >= 4;
}
function render(snapshot) {
  latestSnapshot = snapshot;
  const simulated = snapshot.mode === "simulated";
  const frame = snapshot.latest || {};
  const stale = snapshot.stale;
  controls(snapshot.controls_enabled && !stale);
  for (const button of document.querySelectorAll(".scenario")) {
    const selected = button.dataset.scenario === snapshot.scenario_name;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
  $("scenarioPanel").hidden = !simulated;
  $("sourceBanner").className = "source-banner" + (!simulated ? " hardware" : "") + (stale ? " stale" : "");
  text("sourceTag", simulated ? "DEVELOPMENT SIMULATOR" : "USB HARDWARE");
  text("sourceCopy", snapshot.error || (stale ? "No fresh measurements. Displayed values are the last received data." :
    simulated ? "Illustrative data only. No physical battery is connected." : "Real serial measurements. Hardware controls are read-only here."));
  text("lastSeen", snapshot.age_s === null ? "Waiting for data" : snapshot.age_s < 3 ? "Updated just now" : "Last seen " + Math.floor(snapshot.age_s) + " s ago");
  text("connectionText", stale ? "Awaiting data" : simulated ? "Simulator running" : "Device connected");
  $("connectionDot").className = "status-dot " + (stale ? "stale" : "connected");
  text("socValue", Number.isFinite(frame.soc_pct) && frame.estimate_valid ? fmt(frame.soc_pct, 0) + "%" : "—");
  $("socArc").style.strokeDasharray = (frame.estimate_valid ? Math.max(0, Math.min(100, frame.soc_pct || 0)) : 0) + " 100";
  $("socArc").style.opacity = frame.estimate_valid ? "1" : "0";
  text("runtimeValue", duration(frame.runtime_no_solar_h));
  text("netRuntime", Number.isFinite(frame.runtime_h) ? duration(frame.runtime_h) :
    frame.estimate_valid && Number.isFinite(frame.battery_a) && frame.battery_a < -0.02 ? "Charging" : "—");
  text("energyValue", Number.isFinite(frame.usable_energy_wh) ? fmt(frame.usable_energy_wh) + " Wh" : "—");
  text("reserveValue", Number.isFinite(frame.reserve_pct) ? fmt(frame.reserve_pct, 0) + "%" : "—");
  text("temperatureValue", Number.isFinite(frame.temperature_c) ? fmt(frame.temperature_c) + " °C" : "—");
  text("voltageValue", fmt(frame.battery_v, 2));
  text("loadValue", fmt(frame.load_w, 2));
  text("loadFoot", simulated ? "Includes converter + controller" : "Measured at load-branch input");
  text("solarValue", fmt(frame.solar_w, 2));
  text("currentValue", Number.isFinite(frame.battery_a) ? Math.abs(frame.battery_a).toFixed(3) + " A · " +
    (frame.battery_a < -0.02 ? "charging" : frame.battery_a > 0.02 ? "discharging" : "near idle") : "Current unavailable");
  text("flowState", stale ? "Stale data" : !frame.sensor_ok ? "Check sensors" : frame.battery_a < -0.02 ? "Charging" : "Discharging");
  text("stateTitle", (frame.state || "WAITING").replaceAll("_", " ").toLowerCase().replace(/^./, c => c.toUpperCase()));
  text("stateReason", frame.reason || "Waiting for controller telemetry.");
  $("policyState").className = "policy-state" +
    (["SENSOR_FAULT", "TEMPERATURE"].includes(frame.state) ? " fault" : ["PRIORITY", "RESERVE", "WATCH", "HARDWARE_LOCKED", "UNCALIBRATED"].includes(frame.state) ? " warning" : "");
  if (document.activeElement !== $("runtimeSlider") && Number.isFinite(frame.minimum_runtime_h)) {
    $("runtimeSlider").value = frame.minimum_runtime_h;
    text("sliderValue", fmt(frame.minimum_runtime_h));
  }
  text("essentialStatus", simulated ? "ON" : "Unmetered");
  text("optionalStatus", typeof frame.optional_on === "boolean" ? frame.optional_on ? "ON" : "OFF" : "—");
  $("optionalStatus").className = "load-status" + (!frame.optional_on ? " off" : "");
  text("loadNote", simulated ? "Commands affect the simulator only." :
    "Optional status reports the output command, not independent load feedback. Physical control stays on the ESP32.");
  text("assumptionsText", "4S LiFePO₄ · " + (frame.capacity_ah || 6) + " Ah configured. " +
    (simulated ? "Illustrative model; no accuracy or experimental results are implied." :
      "Capacity, protection limits and calibration must match your actual hardware."));
  text("sampleCount", snapshot.samples + " recorded samples");
  text("logName", snapshot.log_name);
  renderEvents(snapshot.events);
  renderChart(snapshot.history);
}
let polling = false;
async function poll() {
  if (polling) return;
  polling = true;
  try {
    const response = await fetch("/api/state", {signal: AbortSignal.timeout(2500)});
    if (!response.ok) throw new Error("Dashboard connection failed");
    render(await response.json());
  } catch (_) {
    controls(false);
    text("connectionText", "Server disconnected");
    $("connectionDot").className = "status-dot stale";
    $("sourceBanner").classList.add("stale");
    text("sourceCopy", "Local server disconnected. Displayed readings are stale. Restart the launcher to reconnect.");
    text("lastSeen", "No live connection");
    if (latestSnapshot) latestSnapshot.stale = true;
  } finally { polling = false; }
}
$("runtimeSlider").addEventListener("input", e => text("sliderValue", Number(e.target.value).toFixed(1)));
$("runtimeSlider").addEventListener("change", e => command("minimum_runtime", Number(e.target.value)));
$("offButton").addEventListener("click", () => command("optional_off"));
$("restoreButton").addEventListener("click", () => command("restore"));
for (const button of document.querySelectorAll(".scenario")) {
  button.setAttribute("aria-pressed", String(button.classList.contains("selected")));
  button.addEventListener("click", () => command("scenario", button.dataset.scenario));
}
new ResizeObserver(() => { if (latestSnapshot) renderChart(latestSnapshot.history); }).observe($("powerChart").parentElement);
controls(false);
poll();
setInterval(poll, 1000);
