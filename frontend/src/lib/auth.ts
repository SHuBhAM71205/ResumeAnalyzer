export const TOKEN_KEY = "resume-analyzer-token";
export const USER_KEY = "resume-analyzer-user";
export const LAST_RESUME_KEY = "resume-analyzer-last-resume";
export const AUTH_EVENT = "resume-analyzer-auth-change";

export type AuthUser = {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
};

export type StoredResumeMeta = {
  resumeId: string;
  userId: string;
  uploadedAt: string;
};

function isBrowser() {
  return typeof window !== "undefined";
}

function emitAuthChange() {
  if (!isBrowser()) {
    return;
  }

  window.dispatchEvent(new Event(AUTH_EVENT));
}

export function getToken() {
  if (!isBrowser()) {
    return null;
  }

  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.setItem(TOKEN_KEY, token);
  emitAuthChange();
}

export function getStoredUser(): AuthUser | null {
  if (!isBrowser()) {
    return null;
  }

  const value = window.localStorage.getItem(USER_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    clearAuth();
    return null;
  }
}

export function setStoredUser(user: AuthUser) {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  emitAuthChange();
}

export function setAuth(token: string, user: AuthUser) {
  setToken(token);
  setStoredUser(user);
}

export function clearAuth() {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  emitAuthChange();
}

export function getLastResumeMeta(): StoredResumeMeta | null {
  if (!isBrowser()) {
    return null;
  }

  const value = window.localStorage.getItem(LAST_RESUME_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as StoredResumeMeta;
  } catch {
    window.localStorage.removeItem(LAST_RESUME_KEY);
    return null;
  }
}

export function setLastResumeMeta(meta: StoredResumeMeta) {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.setItem(LAST_RESUME_KEY, JSON.stringify(meta));
}

export function clearLastResumeMeta() {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.removeItem(LAST_RESUME_KEY);
}
