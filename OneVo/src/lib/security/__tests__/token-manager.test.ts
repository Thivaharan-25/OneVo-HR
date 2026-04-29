import { describe, it, expect, beforeEach } from 'vitest';
import { tokenManager } from '../token-manager';

describe('tokenManager', () => {
  beforeEach(() => tokenManager.clear());

  it('returns null when no token set', () => {
    expect(tokenManager.get()).toBeNull();
  });

  it('stores and retrieves a token', () => {
    tokenManager.set('abc123', 3600);
    expect(tokenManager.get()).toBe('abc123');
  });

  it('isExpiringSoon returns false for fresh token', () => {
    tokenManager.set('abc123', 3600);
    expect(tokenManager.isExpiringSoon()).toBe(false);
  });

  it('isExpiringSoon returns true when within 60s of expiry', () => {
    tokenManager.set('abc123', 30);
    expect(tokenManager.isExpiringSoon()).toBe(true);
  });

  it('clear wipes the token', () => {
    tokenManager.set('abc123', 3600);
    tokenManager.clear();
    expect(tokenManager.get()).toBeNull();
  });
});
