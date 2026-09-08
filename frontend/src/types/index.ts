/**
 * Shared TypeScript type definitions for the frontend.
 *
 * These mirror the Pydantic schemas from the backend API.
 * Update these when backend schemas change.
 */

// ------------------------------------------------------------------
// Common
// ------------------------------------------------------------------

export type Jurisdiction = "india" | "international";

export type AssessmentStatus =
  | "intake"
  | "clarifying"
  | "analyzing"
  | "complete"
  | "escalated"
  | "failed";

export type ConfidenceLevel = "HIGH" | "MODERATE" | "LIMITED" | "INSUFFICIENT";

// ------------------------------------------------------------------
// Auth
// ------------------------------------------------------------------

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  role: "user" | "admin";
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

// ------------------------------------------------------------------
// Sessions
// ------------------------------------------------------------------

export interface WorkspaceSession {
  id: string;
  user_id: string;
  title: string | null;
  current_jurisdiction: Jurisdiction;
}

// ------------------------------------------------------------------
// Assessments
// ------------------------------------------------------------------

export interface Assessment {
  id: string;
  session_id: string;
  status: AssessmentStatus;
  innovation_description: string;
  classification_data: Record<string, unknown> | null;
  ip_assessment: Record<string, unknown> | null;
  tk_assessment: Record<string, unknown> | null;
  abs_assessment: Record<string, unknown> | null;
  action_plan: Record<string, unknown> | null;
  escalation_brief: Record<string, unknown> | null;
  clarification_history: unknown[] | null;
}

// ------------------------------------------------------------------
// API Error
// ------------------------------------------------------------------

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
