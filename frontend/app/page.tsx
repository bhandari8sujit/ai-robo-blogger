"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/AppShell";
import { ApiError, clearAuthToken, getAuthToken, getCurrentUser, login, register, setAuthToken } from "@/lib/api";
import { AuthUser } from "@/lib/types";

export default function Home() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getAuthToken()) {
      setCheckingSession(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => clearAuthToken())
      .finally(() => setCheckingSession(false));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "register") {
        await register(email, password);
      }
      const token = await login(email, password);
      setAuthToken(token.access_token);
      setUser(await getCurrentUser());
    } catch (caught) {
      setError(
        caught instanceof ApiError && caught.status === 409
          ? "That email is already registered."
          : "Check your email and password.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (checkingSession) {
    return <main className="auth-loading">Opening your studio...</main>;
  }

  if (user) {
    return (
      <AppShell
        email={user.email}
        onLogout={() => {
          clearAuthToken();
          setUser(null);
        }}
      />
    );
  }

  return (
    <main className="auth-shell">
      <section className="auth-intro reveal">
        <p className="eyebrow">Robo Blog Studio</p>
        <h1>Your voice enters here. Your argument leaves clearer.</h1>
        <div className="voice-lines" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <p className="auth-copy">A private workspace for turning spoken fragments into researched, structured drafts.</p>
      </section>

      <section className="auth-form-wrap reveal" aria-labelledby="auth-title">
        <div className="auth-mode" aria-label="Authentication mode">
          <button className={mode === "login" ? "active" : ""} type="button" onClick={() => setMode("login")}>
            Sign in
          </button>
          <button className={mode === "register" ? "active" : ""} type="button" onClick={() => setMode("register")}>
            Create account
          </button>
        </div>
        <h2 id="auth-title">{mode === "login" ? "Return to your draft" : "Open your writing room"}</h2>
        <form onSubmit={handleSubmit}>
          <label className="field-label" htmlFor="email">Email</label>
          <input
            className="field"
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <label className="field-label" htmlFor="password">Password</label>
          <input
            className="field"
            id="password"
            name="password"
            type="password"
            minLength={8}
            maxLength={128}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          {error && <p className="error-text" role="alert">{error}</p>}
          <button className="button button-primary auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Working..." : mode === "login" ? "Enter studio" : "Create account"}
          </button>
        </form>
      </section>
    </main>
  );
}
