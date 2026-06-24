/**
 * Logger utility for frontend console logging with levels and timestamps
 */

const LOG_LEVELS = {
  DEBUG: "DEBUG",
  INFO: "INFO",
  WARN: "WARN",
  ERROR: "ERROR",
};

const LOG_COLORS = {
  DEBUG: "#7F8C8D",
  INFO: "#3498DB",
  WARN: "#F39C12",
  ERROR: "#E74C3C",
};

// Store logs in memory for dev panel
let logHistory = [];
const MAX_LOGS = 500;

function formatTimestamp() {
  const now = new Date();
  return now.toLocaleTimeString("pl-PL", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    fractionalSecondDigits: 3,
  });
}

function addToHistory(level, message, data) {
  logHistory.push({
    timestamp: new Date().toISOString(),
    level,
    message,
    data,
  });

  // Keep only last MAX_LOGS entries
  if (logHistory.length > MAX_LOGS) {
    logHistory = logHistory.slice(-MAX_LOGS);
  }
}

function log(level, message, data) {
  if (
    import.meta.env.PROD &&
    (level === LOG_LEVELS.DEBUG || level === LOG_LEVELS.INFO)
  ) {
    return;
  }
  const timestamp = formatTimestamp();
  const color = LOG_COLORS[level];

  // Console styling
  const style = `color: white; background-color: ${color}; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 11px;`;

  if (data) {
    console.log(
      `%c${level}%c ${timestamp} ${message}`,
      style,
      "color: #666; font-size: 12px;",
      data,
    );
  } else {
    console.log(
      `%c${level}%c ${timestamp} ${message}`,
      style,
      "color: #666; font-size: 12px;",
    );
  }

  addToHistory(level, message, data);
}

export const logger = {
  debug: (message, data) => log(LOG_LEVELS.DEBUG, message, data),
  info: (message, data) => log(LOG_LEVELS.INFO, message, data),
  warn: (message, data) => log(LOG_LEVELS.WARN, message, data),
  error: (message, data) => log(LOG_LEVELS.ERROR, message, data),
  getHistory: () => logHistory,
  clearHistory: () => {
    logHistory = [];
    console.clear();
    console.log("%cLogs cleared", "color: #27AE60; font-weight: bold;");
  },
};

export default logger;
