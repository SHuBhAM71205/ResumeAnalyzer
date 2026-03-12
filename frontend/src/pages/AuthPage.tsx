import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { FileCheck2 } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { getErrorMessage } from "../lib/errors";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(5, "Password must be at least 5 characters"),
});

const signupSchema = loginSchema.extend({
  name: z.string().min(2, "Name must be at least 2 characters"),
});

type LoginForm = z.infer<typeof loginSchema>;
type SignupForm = z.infer<typeof signupSchema>;

export function AuthPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isHydrated, login } = useAuth();
  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
  const signupForm = useForm<SignupForm>({ resolver: zodResolver(signupSchema) });

  if (isHydrated && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const loginMutation = useMutation({
    mutationFn: api.login,
    onSuccess: (data) => {
      login(data.access_token, data.user);
      toast.success("Signed in");
      navigate("/dashboard");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const signupMutation = useMutation({
    mutationFn: api.signup,
    onSuccess: (data) => {
      login(data.access_token, data.user);
      toast.success("Account created");
      navigate("/dashboard");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  return (
    <main className="mx-auto grid min-h-screen max-w-6xl gap-8 px-6 py-8 md:px-10 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="panel flex flex-col justify-between overflow-hidden p-8 md:p-10">
        <div className="space-y-6">
          <span className="eyebrow">Welcome</span>
          <h1 className="font-display text-4xl font-bold tracking-[-0.04em] md:text-5xl">
            Sign in to continue, or create an account in a minute.
          </h1>
          <p className="max-w-lg text-base leading-8 text-ink/68">
            Keep your details and your latest resume in one simple dashboard.
          </p>
        </div>

        <div className="mt-10 rounded-3xl border border-ink/10 bg-ink p-6 text-sand">
          <div className="mb-4 inline-flex rounded-2xl bg-white/10 p-3">
            <FileCheck2 size={20} />
          </div>
          <p className="text-sm uppercase tracking-[0.24em] text-sand/60">What you can do</p>
          <p className="mt-3 text-2xl font-display font-bold">Upload and manage your resume</p>
          <p className="mt-2 text-sm leading-7 text-sand/72">
            Once signed in, you can upload a PDF, update it later, and download or analyze it from your dashboard.
          </p>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <form
          className="panel space-y-5 p-8"
          onSubmit={loginForm.handleSubmit((values) => loginMutation.mutate(values))}
        >
          <div>
            <p className="eyebrow">Sign in</p>
            <h2 className="mt-4 font-display text-3xl font-bold">Welcome back</h2>
          </div>

          <div>
            <label className="label">Email</label>
            <input className="input" {...loginForm.register("email")} placeholder="you@example.com" />
            {loginForm.formState.errors.email ? (
              <p className="mt-2 text-sm text-clay">{loginForm.formState.errors.email.message}</p>
            ) : null}
          </div>

          <div>
            <label className="label">Password</label>
            <input className="input" type="password" {...loginForm.register("password")} placeholder="••••••••" />
            {loginForm.formState.errors.password ? (
              <p className="mt-2 text-sm text-clay">{loginForm.formState.errors.password.message}</p>
            ) : null}
          </div>

          <button className="button-primary w-full" disabled={loginMutation.isPending} type="submit">
            {loginMutation.isPending ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <form
          className="panel space-y-5 p-8"
          onSubmit={signupForm.handleSubmit((values) => signupMutation.mutate(values))}
        >
          <div>
            <p className="eyebrow">Create account</p>
            <h2 className="mt-4 font-display text-3xl font-bold">Create your account</h2>
          </div>

          <div>
            <label className="label">Name</label>
            <input className="input" {...signupForm.register("name")} placeholder="Your name" />
            {signupForm.formState.errors.name ? (
              <p className="mt-2 text-sm text-clay">{signupForm.formState.errors.name.message}</p>
            ) : null}
          </div>

          <div>
            <label className="label">Email</label>
            <input className="input" {...signupForm.register("email")} placeholder="you@example.com" />
            {signupForm.formState.errors.email ? (
              <p className="mt-2 text-sm text-clay">{signupForm.formState.errors.email.message}</p>
            ) : null}
          </div>

          <div>
            <label className="label">Password</label>
            <input className="input" type="password" {...signupForm.register("password")} placeholder="Minimum 8 characters" />
            {signupForm.formState.errors.password ? (
              <p className="mt-2 text-sm text-clay">{signupForm.formState.errors.password.message}</p>
            ) : null}
          </div>

          <button className="button-primary w-full" disabled={signupMutation.isPending} type="submit">
            {signupMutation.isPending ? "Creating..." : "Create account"}
          </button>
        </form>

        <div className="lg:col-span-2">
          <Link to="/" className="button-secondary">
            Back to landing
          </Link>
        </div>
      </section>
    </main>
  );
}
