// CortexHire — Shared TypeScript Types

export interface RoleGenome {
  technical_depth: number;
  ambiguity_tolerance: number;
  ownership: number;
  communication: number;
  startup_readiness: number;
  leadership_potential: number;
  creativity: number;
  execution_speed: number;
  functional_needs: string[];
  hidden_needs: string[];
  team_dynamics: string;
  risk_profile: string;
  cognitive_style: string;
  role_summary: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
  location?: string;
  employment_type?: string;
  seniority?: string;
  created_at: string;
  role_genome?: RoleGenome;
  status: 'pending' | 'processing' | 'ready';
}

export interface CareerRole {
  company: string;
  industry?: string;
  company_size?: string;
  company_type?: string;
  title: string;
  start_year: number;
  end_year: number;
  team_size: number;
  impact_score: number;
  description?: string;
}

export interface Skill {
  name: string;
  proficiency: number;
}

export interface CapabilityProfile {
  technical_depth: number;
  adaptability: number;
  leadership: number;
  execution: number;
  systems_thinking: number;
  creativity: number;
  resilience: number;
  communication: number;
}

export interface TemporalDataPoint {
  year: number;
  company: string;
  title: string;
  impact_score: number;
  team_size: number;
  company_type: string;
}

export interface TemporalProfile {
  trajectory: 'accelerating' | 'steady' | 'plateauing' | 'declining' | 'unknown';
  momentum_score: number;
  impact_trend: number;
  team_growth_trend: number;
  avg_tenure_years: number;
  max_team_led: number;
  avg_impact_score: number;
  impact_momentum: number;
  startup_affinity: number;
  data_points: TemporalDataPoint[];
  total_roles: number;
}

export interface Candidate {
  id: string;
  name: string;
  headline?: string;
  location?: string;
  summary?: string;
  years_experience?: number;
  education_tier?: string;
  education_detail?: string;
  career_history?: CareerRole[];
  skills?: (Skill | string)[];
  achievements?: string[];
  capability_profile?: CapabilityProfile;
  temporal_profile?: TemporalProfile;
}

export interface AgentResult {
  agent: string;
  score: number;
  confidence: number;
  key_signals: string[];
  risks: string[];
  reasoning: string;
  // Bias Corrector specific
  bias_flags_detected?: string[];
  bias_adjustment?: number;
  adjusted_score?: number;
  // Future Predictor specific
  trajectory?: string;
  predicted_role_in_2_years?: string;
  learning_velocity?: number;
  leadership_emergence?: number;
}

export interface AgentScores {
  agent_results: AgentResult[];
  embedding_similarity: number;
  trajectory: string;
  raw_agent_score: number;
}

export interface BiasReport {
  bias_flags: string[];
  raw_adjustment: number;
  bias_risk_score: number;
  has_prestige_halo: boolean;
  has_gap_penalty: boolean;
  has_pedigree_correction: boolean;
  has_geo_correction: boolean;
  recommendation: string;
}

export interface RankedCandidate {
  rank_position: number;
  fit_score: number;
  risk_score: number;
  growth_score: number;
  confidence_score: number;
  success_probability: number;
  explanation?: string;
  agent_scores?: AgentScores;
  bias_report?: BiasReport;
  candidate: Candidate;
}

export interface RankingRun {
  run_id: string;
  job_id: string;
  status: 'pending' | 'processing' | 'complete' | 'failed' | 'no_results';
  total_candidates?: number;
  results: RankedCandidate[];
}

export interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

// ─── Interview Types ─────────────────────────────────────────

export interface InterviewStartResponse {
  session_id: string;
  questions: string[];
  job_title: string;
  company: string;
  candidate_name: string;
}

export interface AnswerScores {
  question_index: number;
  answer_quality: number;
  communication: number;
  posture: number;
  engagement: number;
  confidence: number;
  feedback: {
    strength?: string;
    weakness?: string;
    suggested_followup?: string;
    overall_comment?: string;
    answer_quality?: number;
    communication?: number;
  };
}

export interface FrameAnalysis {
  posture_score: number;
  eye_contact_score: number;
  engagement_score: number;
  confidence_score: number;
  observations: string[];
  overall_body_language: number;
  source: 'gemini' | 'mock' | 'error';
}

export interface InterviewAISummary {
  verdict: 'strong_hire' | 'hire' | 'maybe' | 'no_hire' | 'strong_no_hire';
  headline: string;
  strengths: string[];
  concerns: string[];
  body_language_summary: string;
  recommendation: string;
}

export interface InterviewReport {
  session_id: string;
  candidate_name: string;
  job_title: string;
  company: string;
  total_score: number;
  scores: {
    answer_quality: number;
    communication: number;
    posture: number;
    engagement: number;
    confidence: number;
  };
  ai_summary: InterviewAISummary;
  per_question: Array<{
    question_index: number;
    question_text: string;
    transcript: string;
    answer_quality: number | null;
    communication: number | null;
    posture: number | null;
    engagement: number | null;
    confidence: number | null;
    feedback: AnswerScores['feedback'];
  }>;
}

export interface InterviewSessionSummary {
  id: string;
  job_id: string;
  candidate_name: string;
  status: 'active' | 'complete' | 'abandoned';
  total_score: number | null;
  created_at: string;
}

