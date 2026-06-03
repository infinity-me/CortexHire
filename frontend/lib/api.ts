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
};

// ─── Ranking ─────────────────────────────────────────────────

export const rankingApi = {
  startRun: async (jobId: string, shortlistSize: number = 10): Promise<{ run_id: string }> => {
    const res = await api.post(`/api/ranking/run/${jobId}?shortlist_size=${shortlistSize}`);
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
  // Poll until complete
  pollResults: async (
    runId: string,
    onProgress?: (status: string, count: number) => void,
    maxWait: number = 120000
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
  start: async (jobId: string, candidateName: string, candidateEmail?: string, numQuestions = 6): Promise<InterviewStartResponse> => {
    const res = await api.post('/api/interview/start', {
      job_id: jobId,
      candidate_name: candidateName,
      candidate_email: candidateEmail,
      num_questions: numQuestions,
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

export default api;

