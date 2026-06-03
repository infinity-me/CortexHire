"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic, MicOff, Video, VideoOff, ChevronRight,
  AlertTriangle, CheckCircle, Clock, BarChart2, Eye, Shield, Activity
} from "lucide-react";
import { interviewApi } from "@/lib/api";
import type { AnswerScores, FrameAnalysis } from "@/lib/types";

// Browser Speech Recognition — define types inline since they're not in standard TS lib
interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechRecognitionResultList;
}
interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}
interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}
interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}
interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: ((event: Event) => void) | null;
  start(): void;
  stop(): void;
}
interface ISpeechRecognitionConstructor {
  new(): ISpeechRecognition;
}


// ─── Types ────────────────────────────────────────────────────

interface SessionData {
  session_id: string;
  questions: string[];
  job_title: string;
  company: string;
  candidate_name: string;
}

interface LiveScores {
  posture: number;
  eye_contact: number;
  engagement: number;
  confidence: number;
}

type InterviewPhase = "waiting" | "question" | "processing" | "done";

// ─── Score Meter ─────────────────────────────────────────────

function ScoreMeter({ label, value, color, icon: Icon }: {
  label: string; value: number; color: string; icon: React.ElementType;
}) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--text-secondary)" }}>
          <Icon size={12} color={color} />
          {label}
        </div>
        <div style={{ fontSize: 15, fontWeight: 800, color, fontFamily: "'Space Grotesk', sans-serif" }}>
          {value.toFixed(0)}
        </div>
      </div>
      <div style={{ height: 5, borderRadius: 3, background: "var(--bg-elevated)", overflow: "hidden" }}>
        <motion.div
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ height: "100%", borderRadius: 3, background: color }}
        />
      </div>
    </div>
  );
}

// ─── Waveform ─────────────────────────────────────────────────

function VoiceWave({ active }: { active: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 3, height: 32 }}>
      {Array.from({ length: 12 }).map((_, i) => (
        <motion.div
          key={i}
          animate={active ? {
            height: [4, Math.random() * 24 + 8, 4],
            opacity: [0.4, 1, 0.4],
          } : { height: 4, opacity: 0.2 }}
          transition={active ? {
            duration: 0.5 + Math.random() * 0.5,
            repeat: Infinity,
            delay: i * 0.05,
          } : {}}
          style={{
            width: 3, borderRadius: 2,
            background: active ? "#7c3aed" : "var(--border-default)",
            minHeight: 4,
          }}
        />
      ))}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────

export default function InterviewSessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();

  // Session data
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  // Media
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [micMuted, setMicMuted] = useState(false);

  // Interview state
  const [currentQ, setCurrentQ] = useState(0);
  const [phase, setPhase] = useState<InterviewPhase>("waiting");
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [timeLeft, setTimeLeft] = useState(120); // 2 min per question
  const [completedAnswers, setCompletedAnswers] = useState<AnswerScores[]>([]);

  // Scores
  const [liveScores, setLiveScores] = useState<LiveScores>({ posture: 0, eye_contact: 0, engagement: 0, confidence: 0 });
  const [questionScores, setQuestionScores] = useState<AnswerScores | null>(null);
  const [frameScoreHistory, setFrameScoreHistory] = useState<FrameAnalysis[]>([]);

  // Speech recognition
  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // ─── Load session from URL / localStorage ─────────────────
  useEffect(() => {
    // Try to recover session from sessionStorage (set by setup page via redirect)
    const stored = sessionStorage.getItem(`interview_${sessionId}`);
    if (stored) {
      setSession(JSON.parse(stored));
      setLoading(false);
    } else {
      // Session data not in storage — show minimal UI that still works
      setSession({
        session_id: sessionId,
        questions: [],
        job_title: "",
        company: "",
        candidate_name: "",
      });
      setLoading(false);
    }
  }, [sessionId]);

  // ─── Camera Setup ─────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: true,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraReady(true);
    } catch (e) {
      setCameraError("Camera access denied. Please allow camera/microphone access and reload.");
    }
  }, []);

  useEffect(() => {
    startCamera();
    return () => {
      streamRef.current?.getTracks().forEach(t => t.stop());
      if (timerRef.current) clearInterval(timerRef.current);
      if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
      recognitionRef.current?.stop();
    };
  }, [startCamera]);

  // ─── Speech Recognition ───────────────────────────────────
  const startSpeech = useCallback(() => {
    const SpeechRecognitionAPI: ISpeechRecognitionConstructor | undefined =
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (e: SpeechRecognitionEvent) => {
      let final = "";
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript + " ";
        else interim += e.results[i][0].transcript;
      }
      if (final) setTranscript(prev => prev + final);
      setInterimTranscript(interim);
      setIsSpeaking(interim.length > 0);
    };

    recognition.onerror = () => setIsSpeaking(false);
    recognition.onend = () => setIsSpeaking(false);
    recognitionRef.current = recognition;
    recognition.start();
  }, []);

  const stopSpeech = useCallback(() => {
    recognitionRef.current?.stop();
    setIsSpeaking(false);
    setInterimTranscript("");
  }, []);

  // ─── Frame Capture ────────────────────────────────────────
  const captureFrame = useCallback(async (questionIndex: number, questionText: string) => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = 512;
    canvas.height = 384;
    ctx.drawImage(videoRef.current, 0, 0, 512, 384);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.7);
    const base64 = dataUrl.split(",")[1];

    try {
      const result = await interviewApi.analyzeFrame(sessionId, questionIndex, base64, questionText);
      setFrameScoreHistory(prev => [...prev, result]);
      setLiveScores({
        posture: result.posture_score,
        eye_contact: result.eye_contact_score,
        engagement: result.engagement_score,
        confidence: result.confidence_score,
      });
    } catch (_) {
      // silently ignore frame analysis failures
    }
  }, [sessionId]);

  // ─── Start Question ───────────────────────────────────────
  const startQuestion = useCallback(() => {
    if (!session) return;
    setTranscript("");
    setInterimTranscript("");
    setQuestionScores(null);
    setTimeLeft(120);
    setPhase("question");
    startSpeech();

    // Countdown timer
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // Frame capture every 8s
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
    frameIntervalRef.current = setInterval(() => {
      captureFrame(currentQ, session.questions[currentQ] || "");
    }, 8000);
    // Capture first frame after 3s
    setTimeout(() => captureFrame(currentQ, session.questions[currentQ] || ""), 3000);
  }, [session, currentQ, startSpeech, captureFrame]);

  // Auto-advance when timer hits 0
  useEffect(() => {
    if (timeLeft === 0 && phase === "question") {
      handleNextQuestion();
    }
  }, [timeLeft, phase]);

  // ─── Next Question / Submit Answer ────────────────────────
  const handleNextQuestion = useCallback(async () => {
    if (!session || phase !== "question") return;
    if (timerRef.current) clearInterval(timerRef.current);
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
    stopSpeech();
    setPhase("processing");

    const fullTranscript = transcript.trim();
    const questionText = session.questions[currentQ] || "";

    // Average posture scores for this question
    const avgScore = (arr: number[]) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 55;
    const recent = frameScoreHistory.slice(-3);
    const postureAvg = avgScore(recent.map(f => f.posture_score));
    const engagementAvg = avgScore(recent.map(f => f.engagement_score));
    const confidenceAvg = avgScore(recent.map(f => f.confidence_score));

    try {
      const scores = await interviewApi.evaluateAnswer(
        sessionId, currentQ, questionText, fullTranscript,
        postureAvg, engagementAvg, confidenceAvg,
      );
      setQuestionScores(scores);
      setCompletedAnswers(prev => [...prev, scores]);

      // Show result briefly then advance
      setTimeout(() => {
        const nextQ = currentQ + 1;
        if (nextQ >= session.questions.length) {
          // Done — generate report
          setPhase("done");
          generateFinalReport();
        } else {
          setCurrentQ(nextQ);
          setPhase("waiting");
        }
      }, 3000);
    } catch (e) {
      setPhase("waiting");
    }
  }, [session, phase, transcript, currentQ, frameScoreHistory, sessionId, stopSpeech]);

  const generateFinalReport = async () => {
    try {
      await interviewApi.getReport(sessionId);
      router.push(`/interview/report/${sessionId}`);
    } catch (_) {
      router.push(`/interview/report/${sessionId}`);
    }
  };

  const toggleMic = () => {
    const audioTrack = streamRef.current?.getAudioTracks()[0];
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled;
      setMicMuted(!audioTrack.enabled);
    }
  };

  if (loading || !session) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 48, height: 48, border: "3px solid rgba(124,58,237,0.3)", borderTopColor: "#7c3aed", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 16px" }} />
          <div style={{ color: "var(--text-muted)" }}>Loading interview session...</div>
        </div>
      </div>
    );
  }

  const questions = session.questions;
  const progress = questions.length > 0 ? ((currentQ / questions.length) * 100) : 0;
  const currentQuestion = questions[currentQ] || "";

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
            Live Interview — {session.candidate_name || "Candidate"}
          </h1>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
            {session.job_title} {session.company ? `at ${session.company}` : ""}
          </div>
        </div>
        {/* Progress */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
            Question {Math.min(currentQ + 1, questions.length)} of {questions.length}
          </div>
          <div style={{ width: 120, height: 6, borderRadius: 3, background: "var(--bg-elevated)", overflow: "hidden" }}>
            <div style={{ height: "100%", borderRadius: 3, width: `${progress}%`, background: "linear-gradient(90deg, #7c3aed, #f43f5e)", transition: "width 0.5s ease" }} />
          </div>
        </div>
      </div>

      <div className="session-layout" style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 20 }}>
        {/* Left: Video + Question */}
        <div>
          {/* Video Feed */}
          <div style={{ position: "relative", borderRadius: 16, overflow: "hidden", marginBottom: 16, background: "var(--bg-surface)", border: "1px solid var(--border-default)" }}>
            <video
              ref={videoRef}
              style={{ width: "100%", display: "block", borderRadius: 16, transform: "scaleX(-1)" }}
              muted
              playsInline
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />

            {/* Posture ring overlay */}
            {cameraReady && liveScores.posture > 0 && (
              <div style={{
                position: "absolute", top: 12, left: 12,
                padding: "4px 10px", borderRadius: 20,
                background: "rgba(0,0,0,0.6)",
                border: `2px solid ${liveScores.posture >= 70 ? "#10b981" : liveScores.posture >= 50 ? "#f59e0b" : "#f43f5e"}`,
                fontSize: 11, fontWeight: 700,
                color: liveScores.posture >= 70 ? "#10b981" : liveScores.posture >= 50 ? "#f59e0b" : "#f43f5e",
              }}>
                Posture {liveScores.posture.toFixed(0)}
              </div>
            )}

            {/* Live indicator */}
            {phase === "question" && (
              <div style={{
                position: "absolute", top: 12, right: 12,
                padding: "4px 10px", borderRadius: 20,
                background: "rgba(244,63,94,0.9)",
                fontSize: 11, fontWeight: 700, color: "white",
                display: "flex", alignItems: "center", gap: 5,
              }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "white", animation: "pulse-glow 1s ease-in-out infinite" }} />
                LIVE
              </div>
            )}

            {/* Camera error */}
            {cameraError && (
              <div style={{
                position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
                background: "rgba(0,0,0,0.8)", flexDirection: "column", gap: 12, padding: 24,
              }}>
                <VideoOff size={40} color="#f43f5e" />
                <div style={{ textAlign: "center", color: "var(--text-secondary)", fontSize: 13 }}>{cameraError}</div>
              </div>
            )}

            {/* Timer overlay */}
            {phase === "question" && (
              <div style={{
                position: "absolute", bottom: 12, right: 12,
                padding: "6px 12px", borderRadius: 20,
                background: timeLeft <= 30 ? "rgba(244,63,94,0.9)" : "rgba(0,0,0,0.6)",
                fontSize: 13, fontWeight: 700, color: "white",
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <Clock size={13} />
                {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
              </div>
            )}
          </div>

          {/* Question Card */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
            {phase === "done" ? (
              <div style={{ textAlign: "center", padding: "20px 0" }}>
                <CheckCircle size={40} color="#10b981" style={{ marginBottom: 12 }} />
                <div style={{ fontSize: 18, fontWeight: 700, color: "#10b981", marginBottom: 8 }}>Interview Complete!</div>
                <div style={{ color: "var(--text-muted)", fontSize: 14 }}>Generating your AI report...</div>
              </div>
            ) : (
              <>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                    Question {currentQ + 1}
                  </div>
                  {phase === "processing" && (
                    <div style={{ fontSize: 11, color: "#a78bfa", display: "flex", alignItems: "center", gap: 5 }}>
                      <div style={{ width: 10, height: 10, border: "2px solid rgba(167,139,250,0.3)", borderTopColor: "#a78bfa", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      AI Scoring...
                    </div>
                  )}
                </div>

                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentQ}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    style={{ fontSize: 17, fontWeight: 600, lineHeight: 1.5, marginBottom: 16, color: "var(--text-primary)" }}
                  >
                    {currentQuestion || "Loading question..."}
                  </motion.div>
                </AnimatePresence>

                {/* Transcript */}
                {(phase === "question" || phase === "processing") && (
                  <div style={{
                    minHeight: 80, padding: "12px 14px", borderRadius: 10,
                    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                    fontSize: 13, lineHeight: 1.6, color: "var(--text-secondary)",
                  }}>
                    {transcript || "Start speaking — your words appear here in real time..."}
                    {interimTranscript && (
                      <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>{interimTranscript}</span>
                    )}
                  </div>
                )}

                {/* Controls */}
                <div style={{ display: "flex", gap: 10, marginTop: 16, alignItems: "center" }}>
                  {phase === "waiting" && (
                    <button
                      id="start-answer-btn"
                      onClick={startQuestion}
                      disabled={!cameraReady}
                      style={{
                        flex: 1, padding: "11px 20px",
                        background: "linear-gradient(135deg, #7c3aed, #4338ca)",
                        border: "none", borderRadius: 10, cursor: "pointer",
                        color: "white", fontSize: 14, fontWeight: 700,
                        display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                        opacity: cameraReady ? 1 : 0.5,
                      }}
                    >
                      <Mic size={15} />
                      {currentQ === 0 ? "Start Interview" : "Answer Question"}
                    </button>
                  )}

                  {phase === "question" && (
                    <>
                      <button
                        onClick={toggleMic}
                        title={micMuted ? "Unmute" : "Mute"}
                        style={{
                          padding: "11px 14px", borderRadius: 10,
                          background: micMuted ? "rgba(244,63,94,0.15)" : "var(--bg-elevated)",
                          border: `1px solid ${micMuted ? "rgba(244,63,94,0.3)" : "var(--border-default)"}`,
                          cursor: "pointer", color: micMuted ? "#f43f5e" : "var(--text-secondary)",
                        }}
                      >
                        {micMuted ? <MicOff size={16} /> : <Mic size={16} />}
                      </button>
                      <button
                        id="next-question-btn"
                        onClick={handleNextQuestion}
                        style={{
                          flex: 1, padding: "11px 20px",
                          background: "linear-gradient(135deg, #10b981, #059669)",
                          border: "none", borderRadius: 10, cursor: "pointer",
                          color: "white", fontSize: 14, fontWeight: 700,
                          display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                        }}
                      >
                        {currentQ >= questions.length - 1 ? "Finish Interview" : "Next Question"}
                        <ChevronRight size={15} />
                      </button>
                    </>
                  )}
                </div>

                {/* Voice waveform */}
                {phase === "question" && (
                  <div style={{ marginTop: 12 }}>
                    <VoiceWave active={isSpeaking} />
                  </div>
                )}

                {/* Quick score preview after answer */}
                {phase === "processing" && questionScores && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      marginTop: 14, padding: "12px 14px", borderRadius: 10,
                      background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)",
                    }}
                  >
                    <div style={{ fontSize: 12, color: "#10b981", fontWeight: 700, marginBottom: 6 }}>Answer Scored ✓</div>
                    <div style={{ display: "flex", gap: 16, fontSize: 12, color: "var(--text-secondary)" }}>
                      <span>Quality: <strong style={{ color: "var(--text-primary)" }}>{questionScores.answer_quality.toFixed(0)}</strong></span>
                      <span>Comm: <strong style={{ color: "var(--text-primary)" }}>{questionScores.communication.toFixed(0)}</strong></span>
                      <span>Posture: <strong style={{ color: "var(--text-primary)" }}>{questionScores.posture.toFixed(0)}</strong></span>
                    </div>
                    {questionScores.feedback?.strength && (
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>
                        ✓ {questionScores.feedback.strength}
                      </div>
                    )}
                  </motion.div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right: Live Score Panel */}
        <div>
          {/* Live Body Language */}
          <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 16 }}>
              Live Body Language
            </div>
            <ScoreMeter label="Posture" value={liveScores.posture} color="#10b981" icon={Activity} />
            <ScoreMeter label="Eye Contact" value={liveScores.eye_contact} color="#06b6d4" icon={Eye} />
            <ScoreMeter label="Engagement" value={liveScores.engagement} color="#7c3aed" icon={BarChart2} />
            <ScoreMeter label="Confidence" value={liveScores.confidence} color="#f59e0b" icon={Shield} />
            {frameScoreHistory.length === 0 && (
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
                Analysis starts 3s after question begins
              </div>
            )}
            {frameScoreHistory.length > 0 && (
              <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 8, textAlign: "right" }}>
                {frameScoreHistory[frameScoreHistory.length - 1].source === "gemini" ? "🟢 Gemini Vision" : "⚪ Mock Analysis"}
              </div>
            )}
          </div>

          {/* Question Progress */}
          <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 14 }}>
              Progress
            </div>
            {questions.map((q, i) => {
              const answered = completedAnswers[i];
              const isCurrent = i === currentQ;
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 10, marginBottom: 8,
                  padding: "8px 10px", borderRadius: 8,
                  background: isCurrent ? "rgba(124,58,237,0.15)" : "transparent",
                  border: isCurrent ? "1px solid rgba(124,58,237,0.25)" : "1px solid transparent",
                }}>
                  <div style={{
                    width: 22, height: 22, borderRadius: "50%",
                    background: answered ? "#10b981" : isCurrent ? "#7c3aed" : "var(--bg-elevated)",
                    border: `2px solid ${answered ? "#10b981" : isCurrent ? "#7c3aed" : "var(--border-default)"}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 10, fontWeight: 800, color: "white", flexShrink: 0,
                  }}>
                    {answered ? "✓" : i + 1}
                  </div>
                  <div style={{ fontSize: 11, color: answered ? "#10b981" : isCurrent ? "var(--text-primary)" : "var(--text-muted)", lineHeight: 1.3, flex: 1 }}>
                    {q.length > 50 ? q.slice(0, 50) + "…" : q}
                  </div>
                  {answered && (
                    <div style={{ fontSize: 12, fontWeight: 800, color: answered.answer_quality >= 70 ? "#10b981" : answered.answer_quality >= 50 ? "#f59e0b" : "#f43f5e", fontFamily: "'Space Grotesk', sans-serif" }}>
                      {answered.answer_quality.toFixed(0)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Tips */}
          {phase === "waiting" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card"
              style={{ padding: 16 }}
            >
              <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>Tips</div>
              {[
                "Sit up straight — posture is scored",
                "Look directly at your camera",
                "Use specific examples (STAR method)",
                "Speak clearly and at a measured pace",
              ].map((tip, i) => (
                <div key={i} style={{ fontSize: 11, color: "var(--text-secondary)", marginBottom: 5, display: "flex", gap: 6 }}>
                  <span style={{ color: "#a78bfa" }}>→</span>
                  {tip}
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse-glow { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
      `}</style>
    </div>
  );
}
