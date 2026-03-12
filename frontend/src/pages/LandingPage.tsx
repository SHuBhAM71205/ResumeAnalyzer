import { ArrowRight, CheckCircle2, FileText, UploadCloud } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const features = [
  {
    icon: CheckCircle2,
    title: "Simple and secure",
    body: "Your account stays protected while you upload and manage your resume.",
  },
  {
    icon: UploadCloud,
    title: "Easy resume upload",
    body: "Upload your PDF in a few clicks and keep everything in one place.",
  },
  {
    icon: FileText,
    title: "Ready for insights",
    body: "Use the app to upload, update, download, and analyze your latest resume.",
  },
];

export function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <main className="relative mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8 md:px-10">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="eyebrow">Resume Analyzer</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to={isAuthenticated ? "/dashboard" : "/auth"} className="button-secondary">
            {isAuthenticated ? "Session active" : "Sign in"}
          </Link>
          <Link to="/dashboard" className="button-primary">
            Open dashboard
          </Link>
        </div>
      </header>

      <section className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-7">
          <div className="space-y-4">
            <span className="eyebrow">Your resume, in one place</span>
            <h1 className="max-w-3xl font-display text-5xl font-bold leading-[0.98] tracking-[-0.04em] md:text-6xl">
              Upload, manage, and review your resume with ease.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-ink/72">
              Sign in, keep your profile in one place, and work with your latest resume without
              dealing with a cluttered interface.
            </p>
          </div>

          <div className="flex flex-wrap gap-4">
            <Link to="/auth" className="button-primary gap-2">
              Get started
              <ArrowRight size={16} />
            </Link>
            <Link to="/dashboard" className="button-secondary">Go to dashboard</Link>
          </div>
        </div>

        <div className="panel relative overflow-hidden p-8 md:p-10">
          <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(217,122,58,0.12),transparent_42%,rgba(31,108,99,0.14))]" />
          <div className="relative space-y-6">
            <div className="rounded-3xl border border-white/60 bg-white/80 p-6">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-ink/45">
                Why people use it
              </p>
              <p className="mt-3 text-3xl font-display font-bold">A cleaner way to handle resumes</p>
              <p className="mt-3 text-sm leading-7 text-ink/65">
                Everything important is easy to find: your profile, your uploaded file, and the
                actions you need most.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              {features.map(({ icon: Icon, title, body }) => (
                <article key={title} className="rounded-3xl border border-ink/10 bg-sand/80 p-5">
                  <div className="mb-4 inline-flex rounded-2xl bg-ink p-3 text-sand">
                    <Icon size={18} />
                  </div>
                  <h2 className="font-display text-xl font-bold">{title}</h2>
                  <p className="mt-2 text-sm leading-7 text-ink/65">{body}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
