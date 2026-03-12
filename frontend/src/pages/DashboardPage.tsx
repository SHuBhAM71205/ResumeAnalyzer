import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  Download,
  FileBadge2,
  LogOut,
  RefreshCw,
  Upload,
  UserRound,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import {
  clearLastResumeMeta,
  getLastResumeMeta,
  setLastResumeMeta,
} from "../lib/auth";
import { getErrorMessage } from "../lib/errors";

export function DashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [lastResumeId, setLastResumeId] = useState<string | null>(getLastResumeMeta()?.resumeId ?? null);
  const { logout, updateUser, user } = useAuth();

  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: api.getProfile,
    initialData: user ?? undefined,
    staleTime: 60_000,
    enabled: Boolean(user),
  });

  const profile = profileQuery.data ?? user;

  useEffect(() => {
    if (profileQuery.data) {
      updateUser(profileQuery.data);
    }
  }, [profileQuery.data, updateUser]);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!profile?.id || !selectedFile) {
        throw new Error("Select a PDF before uploading.");
      }

      return api.uploadResume(profile.id, selectedFile);
    },
    onSuccess: (data) => {
      toast.success(data.message);
      const meta = {
        resumeId: data.resume_id,
        userId: profile!.id,
        uploadedAt: new Date().toISOString(),
      };
      setLastResumeMeta(meta);
      setLastResumeId(data.resume_id);
      setSelectedFile(null);
      void queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      if (!lastResumeId || !selectedFile) {
        throw new Error("Select a PDF and make sure a resume has been uploaded first.");
      }

      return api.updateResume(lastResumeId, selectedFile);
    },
    onSuccess: (data) => {
      toast.success(data.message);
      setSelectedFile(null);
      setLastResumeId(data.resume_id);
      if (profile) {
        setLastResumeMeta({
          resumeId: data.resume_id,
          userId: profile.id,
          uploadedAt: new Date().toISOString(),
        });
      }
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      if (!lastResumeId) {
        throw new Error("Upload a resume first so there is a resume id to analyze.");
      }

      return api.analyzeResume(lastResumeId);
    },
    onSuccess: (data) => {
      toast.success(data.message);
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const downloadMutation = useMutation({
    mutationFn: async () => {
      if (!profile?.id) {
        throw new Error("Profile is unavailable.");
      }

      const response = await api.getResume(profile.id);
      return response.blob();
    },
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "resume.pdf";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      toast.success("Resume downloaded");
    },
    onError: (error) => toast.error(getErrorMessage(error)),
  });

  const handleLogout = () => {
    logout();
    navigate("/auth");
  };

  const handleForgetResume = () => {
    clearLastResumeMeta();
    setLastResumeId(null);
    toast.success("Local resume reference cleared");
  };

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-8 md:px-10">
      <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <span className="eyebrow">Dashboard</span>
          <h1 className="mt-4 font-display text-4xl font-bold tracking-[-0.04em] md:text-5xl">
            Manage your resume in one simple place.
          </h1>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link to="/" className="button-secondary">
            Home
          </Link>
          <button className="button-secondary gap-2" onClick={handleLogout} type="button">
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </header>

      <section className="grid gap-6 xl:grid-cols-[0.78fr_1.22fr]">
        <article className="panel p-8">
          <div className="mb-6 flex items-center gap-4">
            <div className="rounded-3xl bg-ink p-4 text-sand">
              <UserRound size={22} />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-ink/45">Your details</p>
              <h2 className="font-display text-2xl font-bold">Profile</h2>
            </div>
          </div>

          {profile ? (
            <dl className="grid gap-4">
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <dt className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/45">Name</dt>
                <dd className="mt-2 text-lg font-semibold">{profile.name}</dd>
              </div>
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <dt className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/45">Email</dt>
                <dd className="mt-2 text-lg font-semibold">{profile.email}</dd>
              </div>
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <dt className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/45">Account ID</dt>
                <dd className="mt-2 break-all text-sm font-semibold text-ink/72">{profile.id}</dd>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-ink/60">
              {profileQuery.isLoading ? "Loading profile..." : "Profile unavailable."}
            </p>
          )}

          <div className="mt-6 rounded-3xl border border-ink/10 bg-sand/75 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/45">Good to know</p>
            <p className="mt-2 text-sm text-ink/68">
              Your dashboard is private to your account, so only you can access your files here.
            </p>
          </div>
        </article>

        <div className="grid gap-6">
          <article className="panel p-8">
            <div className="mb-6 flex items-center gap-4">
              <div className="rounded-3xl bg-ember p-4 text-white">
                <Upload size={22} />
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-ink/45">Upload</p>
                <h2 className="font-display text-2xl font-bold">Add your resume</h2>
              </div>
            </div>

            <div className="rounded-3xl border border-dashed border-ink/15 bg-white/60 p-6">
              <label className="label">PDF file</label>
              <input
                accept="application/pdf"
                className="input"
                type="file"
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
              />
              <p className="mt-3 text-sm text-ink/55">
                PDF files only.
              </p>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              <button
                className="button-primary"
                disabled={!selectedFile || uploadMutation.isPending || !profile?.id}
                onClick={() => uploadMutation.mutate()}
                type="button"
              >
                {uploadMutation.isPending ? "Uploading..." : "Upload resume"}
              </button>
              <button
                className="button-secondary"
                disabled={!selectedFile || updateMutation.isPending || !lastResumeId}
                onClick={() => updateMutation.mutate()}
                type="button"
              >
                {updateMutation.isPending ? "Updating..." : "Replace current resume"}
              </button>
              {selectedFile ? (
                <p className="text-sm text-ink/65">{selectedFile.name}</p>
              ) : (
                <p className="text-sm text-ink/45">Select a PDF to continue.</p>
              )}
            </div>
          </article>

          <article className="panel p-8">
            <div className="mb-6 flex items-center gap-4">
              <div className="rounded-3xl bg-tide p-4 text-white">
                <FileBadge2 size={22} />
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-ink/45">Quick actions</p>
                <h2 className="font-display text-2xl font-bold">Use your saved resume</h2>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <button
                className="rounded-3xl border border-ink/10 bg-white/70 p-5 text-left transition hover:-translate-y-1"
                disabled={downloadMutation.isPending || !profile?.id}
                onClick={() => downloadMutation.mutate()}
                type="button"
              >
                <Download className="mb-4 text-ember" size={20} />
                <p className="font-display text-xl font-bold">Download</p>
                <p className="mt-2 text-sm text-ink/62">Download your saved PDF anytime.</p>
              </button>

              <button
                className="rounded-3xl border border-ink/10 bg-white/70 p-5 text-left transition hover:-translate-y-1"
                disabled={analyzeMutation.isPending || !lastResumeId}
                onClick={() => analyzeMutation.mutate()}
                type="button"
              >
                <Activity className="mb-4 text-tide" size={20} />
                <p className="font-display text-xl font-bold">Analyze</p>
                <p className="mt-2 text-sm text-ink/62">Run analysis on the most recent resume you uploaded.</p>
              </button>

              <button
                className="rounded-3xl border border-ink/10 bg-white/70 p-5 text-left transition hover:-translate-y-1"
                onClick={handleForgetResume}
                type="button"
              >
                <RefreshCw className="mb-4 text-ink" size={20} />
                <p className="font-display text-xl font-bold">Clear saved state</p>
                <p className="mt-2 text-sm text-ink/62">Remove the saved resume reference from this browser.</p>
              </button>
            </div>

            <div className="mt-6 rounded-3xl border border-ink/10 bg-sand/80 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/45">Latest saved resume</p>
              <p className="mt-2 break-all text-sm font-semibold text-ink/72">
                {lastResumeId ?? "No resume saved yet. Upload one to get started."}
              </p>
            </div>
          </article>

          <article className="panel p-8">
            <div className="mb-4">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-ink/45">Helpful information</p>
                <h2 className="mt-2 font-display text-2xl font-bold">What this dashboard gives you</h2>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <p className="font-display text-xl font-bold">Private access</p>
                <p className="mt-2 text-sm text-ink/62">
                  Your files and actions stay tied to your own account.
                </p>
              </div>
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <p className="font-display text-xl font-bold">Easy updates</p>
                <p className="mt-2 text-sm text-ink/62">
                  Replace your latest resume without starting over from scratch.
                </p>
              </div>
              <div className="rounded-3xl border border-ink/10 bg-white/70 p-5">
                <p className="font-display text-xl font-bold">Quick actions</p>
                <p className="mt-2 text-sm text-ink/62">
                  Download or analyze your latest resume in a single tap.
                </p>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
