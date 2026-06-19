// CortexHire — Backend API Client

import axios from 'axios';
import type { Job, RankedCandidate, RankingRun, Candidate, CopilotMessage, InterviewStartResponse, AnswerScores, FrameAnalysis, InterviewReport, InterviewSessionSummary } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 min for ranking pipelines
});

// ─── Jobs ────────────────────────────────────────────────────

export const jobsApi = {
  list: async (): Promise<Job[]> => {
    const res = await api.get('/api/jobs/');
    return res.data;
  },
  get: async (id: string): Promise<Job> => {
    const res = await api.get(`/api/jobs/${id}`);
    return res.data;
  },
  create: async (data: Partial<Job>): Promise<Job> => {
    const res = await api.post('/api/jobs/', data);
    return res.data;
  },
  analyze: async (id: string): Promise<Job> => {
    const res = await api.post(`/api/jobs/${id}/analyze`);
    return res.data;
  },
};

// ─── Candidates ──────────────────────────────────────────────

export const candidatesApi = {
  list: async (): Promise<Candidate[]> => {
    const res = await api.get('/api/candidates/');
    return res.data;
  },
  get: async (id: string): Promise<Candidate> => {
    const res = await api.get(`/api/candidates/${id}`);
    return res.data;
  },
  count: async (): Promise<number> => {
    const res = await api.get('/api/candidates/count/total');
    return res.data.total;
  },
  bulkUpload: async (files: File[]): Promise<{
    total: number; succeeded: number; failed: number;
    results: Array<{ filename: string; status: string; name?: string; headline?: string; candidate_id?: string; error?: string; }>
  }> => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const res = await api.post('/api/candidates/bulk-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 5 min for large batches
    });
    return res.data;
  },
  importDataset: async (file: File, limit: number = 500): Promise<{
    import_id: string; status: string; filename: string; limit: number; message: string;
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('limit', String(limit));
    const res = await api.post(`/api/candidates/import-dataset?limit=${limit}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // upload timeout only — actual import is async
    });
    return res.data;
  },
  getImportStatus: async (importId: string): Promise<{
    import_id: string; status: string; imported: number; filename: string; error?: string;
  }> => {
    const res = await api.get(`/api/candidates/import-status/${importId}`);
    return res.data;
  },
  pollImportStatus: async (
    importId: string,
    onProgress?: (status: string, imported: number) => void,
    maxWait: number = 600000
  ): Promise<{ imported: number }> => {
    const start = Date.now();
    while (Date.now() - start < maxWait) {
      const s = await candidatesApi.getImportStatus(importId);
      onProgress?.(s.status, s.imported);
      if (s.status === 'complete') return { imported: s.imported };
      if (s.status === 'failed') throw new Error(s.error || 'Import failed');
      await new Promise(r => setTimeout(r, 2000));
    }
    throw new Error('Import timed out');
  },
};

// ─── Ranking ─────────────────────────────────────────────────

export const rankingApi = {
  startRun: async (jobId: string, shortlistSize: number = 10, preFilterLimit: number = 100): Promise<{ run_id: string; pre_filter_limit: number }> => {
    const res = await api.post(`/api/ranking/run/${jobId}?shortlist_size=${shortlistSize}&pre_filter_limit=${preFilterLimit}`);
    return res.data;
  },
  getStatus: async (runId: string): Promise<{ run_id: string; status: string; total_candidates: number }> => {
    const res = await api.get(`/api/ranking/run/${runId}/status`);
    return res.data;
  },
  getResults: async (runId: string): Promise<RankingRun> => {
    const res = await api.get(`/api/ranking/results/${runId}`);
    return res.data;
  },
  getLatest: async (jobId: string): Promise<RankingRun> => {
    const res = await api.get(`/api/ranking/job/${jobId}/latest`);
    return res.data;
  },
  listRuns: async (jobId: string): Promise<Array<{
    run_id: string; status: string; total_candidates: number;
    shortlist_size: number; created_at: string;
  }>> => {
    const res = await api.get(`/api/ranking/job/${jobId}/runs`);
    return res.data;
  },
  downloadCsv: (runId: string) => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.open(`${API_BASE}/api/ranking/results/${runId}/download`, '_blank');
  },
  // Poll until complete
  pollResults: async (
    runId: string,
    onProgress?: (status: string, count: number) => void,
    maxWait: number = 600000 // 10 min — enough for large candidate pools
  ): Promise<RankingRun> => {
    const start = Date.now();
    while (Date.now() - start < maxWait) {
      const status = await rankingApi.getStatus(runId);
      onProgress?.(status.status, status.total_candidates);
      if (status.status === 'complete') {
        return await rankingApi.getResults(runId);
      }
      if (status.status === 'failed') {
        throw new Error('Ranking pipeline failed');
      }
      // prefiltering and processing are both valid in-progress states
      await new Promise(r => setTimeout(r, 2000));
    }
    throw new Error('Ranking timed out');
  },
};

// ─── Copilot ─────────────────────────────────────────────────

export const copilotApi = {
  chat: async (jobId: string, message: string, runId?: string): Promise<{ response: string }> => {
    const res = await api.post('/api/copilot/chat', {
      message,
      job_id: jobId,
      run_id: runId,
    });
    return res.data;
  },
  getHistory: async (jobId: string): Promise<CopilotMessage[]> => {
    const res = await api.get(`/api/copilot/history/${jobId}`);
    return res.data;
  },
};

// ─── Health ──────────────────────────────────────────────────

export const healthApi = {
  check: async (): Promise<{ status: string; llm: string }> => {
    const res = await api.get('/health');
    return res.data;
  },
};

// ─── Interview ────────────────────────────────────────────────

export const interviewApi = {
  parseResume: async (file: File): Promise<{ filename: string; text: string; word_count: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/api/interview/parse-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  start: async (
    jobId: string,
    candidateName: string,
    candidateEmail?: string,
    numQuestions = 6,
    customRoleTitle?: string,
    customCompany?: string,
    customDescription?: string,
    resumeContext?: string,
  ): Promise<InterviewStartResponse> => {
    const res = await api.post('/api/interview/start', {
      job_id: jobId,
      candidate_name: candidateName,
      candidate_email: candidateEmail,
      num_questions: numQuestions,
      custom_role_title: customRoleTitle,
      custom_company: customCompany,
      custom_description: customDescription,
      resume_context: resumeContext,
    });
    return res.data;
  },

  evaluateAnswer: async (
    sessionId: string,
    questionIndex: number,
    questionText: string,
    transcript: string,
    postureScore?: number,
    engagementScore?: number,
    confidenceScore?: number,
  ): Promise<AnswerScores> => {
    const res = await api.post('/api/interview/evaluate-answer', {
      session_id: sessionId,
      question_index: questionIndex,
      question_text: questionText,
      transcript,
      posture_score: postureScore,
      engagement_score: engagementScore,
      confidence_score: confidenceScore,
    });
    return res.data;
  },

  analyzeFrame: async (sessionId: string, questionIndex: number, imageBase64: string, currentQuestion: string): Promise<FrameAnalysis> => {
    const res = await api.post('/api/interview/analyze-frame', {
      session_id: sessionId,
      question_index: questionIndex,
      image_base64: imageBase64,
      current_question: currentQuestion,
    });
    return res.data;
  },

  getReport: async (sessionId: string): Promise<InterviewReport> => {
    const res = await api.post(`/api/interview/report/${sessionId}`);
    return res.data;
  },

  listSessions: async (): Promise<InterviewSessionSummary[]> => {
    const res = await api.get('/api/interview/sessions');
    return res.data;
  },
};

// ─── Challenge ────────────────────────────────────────────────

export const challengeApi = {
  getInfo: async (): Promise<{
    full_dataset: { path: string; size_mb: number; estimated_candidates: number; available: boolean } | null;
    sample_dataset: { path: string; candidate_count: number; available: boolean } | null;
    job_description_summary: {
      title: string; company: string; experience: string;
      must_have: string[]; disqualifiers: string[]; key_behavioral_signals: string[];
    };
    scoring_info: { skills_weight: string; career_weight: string; behavioral_weight: string; engagement_weight: string };
  }> => {
    const res = await api.get('/api/challenge/info');
    return res.data;
  },

  run: async (useSample = false, sampleLimit = 0): Promise<{
    run_id: string; status: string; file: string; is_sample: boolean; message: string;
  }> => {
    const res = await api.post(
      `/api/challenge/run?use_sample=${useSample}&sample_limit=${sampleLimit}`,
      {},
      { timeout: 30000 }
    );
    return res.data;
  },

  uploadAndRun: async (
    file: File,
    limit = 0,
    onProgress?: (percent: number) => void
  ): Promise<{
    run_id: string; status: string; filename: string;
    candidate_count: number; is_sample: boolean; message: string;
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('limit', String(limit));
    const res = await api.post('/api/challenge/upload-and-run', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000, // 10 min
      onUploadProgress: (e) => {
        if (e.total) onProgress?.(Math.round((e.loaded / e.total) * 100));
      },
    });
    return res.data;
  },

  getStatus: async (runId: string): Promise<{
    run_id: string; status: string; total_candidates: number; processed: number;
    honeypots_detected: number; started_at: string; completed_at: string | null;
    elapsed_seconds: number | null; error: string | null;
    top_10_preview: Array<{
      rank: number; candidate_id: string; score: number; title: string; name: string;
      skills_score: number; career_score: number; behavioral_score: number;
      engagement_score: number; total_score: number; reasoning: string;
    }>;
    is_sample: boolean;
  }> => {
    const res = await api.get(`/api/challenge/status/${runId}`);
    return res.data;
  },

  getResults: async (runId: string): Promise<{
    run_id: string; status: string; results: Array<{
      rank: number; candidate_id: string; score: number; title: string; name: string;
      skills_score: number; career_score: number; behavioral_score: number;
      engagement_score: number; total_score: number; reasoning: string;
    }>;
    total_candidates: number; honeypots_detected: number;
  }> => {
    const res = await api.get(`/api/challenge/results/${runId}`);
    return res.data;
  },

  download: (runId: string) => {
    const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.open(`${BASE}/api/challenge/download/${runId}`, '_blank');
  },

  pollStatus: async (
    runId: string,
    onProgress?: (processed: number, total: number, honeypots: number, status: string) => void,
    maxWait = 600000
  ) => {
    const start = Date.now();
    while (Date.now() - start < maxWait) {
      const s = await challengeApi.getStatus(runId);
      onProgress?.(s.processed, s.total_candidates, s.honeypots_detected, s.status);
      if (s.status === 'complete') return s;
      if (s.status === 'failed') throw new Error(s.error || 'Challenge ranking failed');
      await new Promise(r => setTimeout(r, 1500));
    }
    throw new Error('Challenge ranking timed out');
  },
};

export default api;


