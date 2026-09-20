const process = require("node:process");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const PORT = process.env.PORT || 3000;
const MAX_PAYLOAD_SIZE = 2 * 1024 * 1024;

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  const reqUrl = req.url.split("?")[0];

  if (req.method === "POST" && (reqUrl === "/api/sync" || reqUrl === "/api/incentives/sync")) {
    let body = "";
    let sizeExceeded = false;

    req.on("data", chunk => {
      body += chunk;
      if (body.length > MAX_PAYLOAD_SIZE) {
        sizeExceeded = true;
        res.writeHead(413, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Payload exceeds 2MB limit" }));
        req.destroy();
      }
    });

    req.on("end", () => {
      if (sizeExceeded) return;
      try {
        const payload = JSON.parse(body);
        payload.serverReceivedTime = new Date().toISOString();

        const logPath = path.join(__dirname, "sync_records.json");
        let existingLogs = [];
        if (fs.existsSync(logPath)) {
          const raw = fs.readFileSync(logPath, "utf8");
          existingLogs = JSON.parse(raw || "[]");
        }

        existingLogs.push(payload);
        fs.writeFileSync(logPath, JSON.stringify(existingLogs, null, 2), "utf8");

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          status: "SUCCESS",
          syncedBookings: payload.bookings ? payload.bookings.length : 0,
          syncedCallLogs: payload.callLogs ? payload.callLogs.length : 0,
          timestamp: payload.serverReceivedTime
        }));
      } catch (_err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid JSON format" }));
      }
    });
  } else {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Endpoint not found" }));
  }
});

server.listen(PORT, () => {
  console.log(`Sync Server running on port ${PORT}`);
});
