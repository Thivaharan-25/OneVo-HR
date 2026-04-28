const IDLE_MS = 30 * 60 * 1000;
let _timer: ReturnType<typeof setTimeout> | null = null;
let _onTimeout: (() => void) | null = null;

function reset() {
  if (_timer) clearTimeout(_timer);
  if (!_onTimeout) return;
  _timer = setTimeout(_onTimeout, IDLE_MS);
}

export const idleTimeout = {
  start(onTimeout: () => void): void {
    _onTimeout = onTimeout;
    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'];
    events.forEach(e => window.addEventListener(e, reset, { passive: true }));
    reset();
  },
  stop(): void {
    if (_timer) { clearTimeout(_timer); _timer = null; }
    _onTimeout = null;
  },
};
