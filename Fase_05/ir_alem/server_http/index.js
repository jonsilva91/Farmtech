const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();

// vamos ler o corpo como texto para poder tratar 'nan'/'NaN' e afins
app.use(express.text({ type: "*/*", limit: "1mb" }));

const RAW_DIR = path.resolve(__dirname, "..", "data", "raw");
const OUT = path.join(RAW_DIR, "telemetry.jsonl");
fs.mkdirSync(RAW_DIR, { recursive: true });

app.get("/health", (req, res) => {
  res.json({ ok: true, ts: new Date().toISOString() });
});

app.post("/ingest", (req, res) => {
  try {
    let body = (req.body || "").toString().trim();

    // saneia JSON inválido vindo do ESP32 (nan/NaN/Infinity) -> null
    body = body
      .replace(/\bNaN\b/gi, "null")
      .replace(/\bInfinity\b/gi, "null")
      .replace(/\b-Infinity\b/gi, "null");

    const obj = JSON.parse(body); // se falhar, vai pro catch
    fs.appendFileSync(OUT, JSON.stringify(obj) + "\n", "utf8");
    return res.json({ ok: true });
  } catch (e) {
    return res.status(400).json({ ok: false, error: String(e) });
  }
});

const PORT = 5000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Listening on http://0.0.0.0:${PORT}`);
});

const LATEST = path.join(RAW_DIR, "latest.json");
const INF = path.join(RAW_DIR, "inference.jsonl");

// recebe uma inferência do Python
app.post("/inference", (req, res) => {
  try {
    let body = (req.body || "").toString().trim();
    body = body
      .replace(/\bNaN\b/gi, "null")
      .replace(/\b-?Infinity\b/gi, "null");
    const obj = JSON.parse(body);
    fs.appendFileSync(INF, JSON.stringify(obj) + "\n", "utf8");
    fs.writeFileSync(LATEST, JSON.stringify(obj, null, 2), "utf8");
    return res.json({ ok: true });
  } catch (e) {
    return res.status(400).json({ ok: false, error: String(e) });
  }
});

// expõe a última classificação
app.get("/latest", (req, res) => {
  try {
    if (!fs.existsSync(LATEST)) return res.json({ ok: true, data: null });
    const data = JSON.parse(fs.readFileSync(LATEST, "utf8"));
    return res.json({ ok: true, data });
  } catch (e) {
    return res.status(500).json({ ok: false, error: String(e) });
  }
});
