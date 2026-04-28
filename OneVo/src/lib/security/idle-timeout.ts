const IDLE_MS = 30 * 60 * 1000;
let _timer: ReturnType<typeof setTimeout> | null = null;
let _onTimeout: (() => void) | null = null;

function reset() {
  if (_timer) clearTimeout(_timer);
  if (!_onTimeout) return;
  _timer = setTimeout(_onTimeout, IDLE_MS);
}

const EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'] as const;

export const idleTimeout = {
  start(onTimeout: () => void): void {
    idleTimeout.stop();
    _onTimeout = onTimeout;
    EVENTS.forEach(e => window.addEventListener(e, reset, { passive: true }));
    reset();
  },
  stop(): void {
    if (_timer) { clearTimeout(_timer); _timer = null; }
    EVENTS.forEach(e => window.removeEventListener(e, reset));
    _onTimeout = null;
  },
};
