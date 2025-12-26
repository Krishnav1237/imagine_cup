const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const REQUEST_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 2;

// ============ Types ============

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

export interface ContentItem {
  id: number;
  title: string;
  source_type: string;
  source_url?: string;
  thumbnail_url?: string;

  status: string;
  stage?: string | null;

  error_message?: string;
  chunk_count?: number;
  completed_chunks?: number;
  progress_percentage?: number;

  created_at: string;
  processed_at?: string | null;
}

export interface ContentChunk {
  id: number;
  sequence_number: number;

  title: string;
  summary?: string;
  text_content?: string;

  source_file?: string;
  source_page?: number;
  source_slide?: number;

  generation_model?: string;
  generation_strategy?: string;

  key_concepts?: string[];
  quiz_questions?: QuizQuestion[];

  difficulty_level?: string;
  visual_context?: string;
  key_frame_timestamp?: number;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
}

export interface GamificationStats {
  focus_coins: number;
  current_streak: number;
  longest_streak: number;
  total_sprints_completed: number;
}

export interface ShopItem {
  id: string;
  name: string;
  type: string;
  rarity: string;
  price: number;
  description: string;
  affordable: boolean;
}

// ============ Error Classes ============

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class AuthError extends ApiError {
  constructor(message: string = "Authentication required") {
    super(message, 401, "AUTH_ERROR");
    this.name = "AuthError";
  }
}

// ============ Helpers ============

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem("focus_token");
}

function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem("focus_token");
  }
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function authFetch(url: string, options: RequestInit = {}, retries = MAX_RETRIES): Promise<any> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  // Add timeout using AbortController
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    // Handle token expiry
    if (res.status === 401) {
      clearAuth();
      throw new AuthError("Session expired. Please log in again.");
    }

    // Handle server errors with retry
    if (res.status >= 500 && retries > 0) {
      console.warn(`Server error ${res.status}, retrying... (${retries} left)`);
      await sleep(1000 * (MAX_RETRIES - retries + 1)); // Exponential backoff
      return authFetch(url, options, retries - 1);
    }

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new ApiError(
        data.detail || `Request failed: ${res.status}`,
        res.status,
        data.code
      );
    }

    return res.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Handle network errors with retry
    if (error instanceof TypeError && error.message.includes("fetch") && retries > 0) {
      console.warn(`Network error, retrying... (${retries} left)`);
      await sleep(1000);
      return authFetch(url, options, retries - 1);
    }
    
    // Handle timeout
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timeout", 408, "TIMEOUT");
    }
    
    throw error;
  }
}

// ============ Auth ============

export async function registerUser(payload: RegisterPayload) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Registration failed");
  }

  return res.json();
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Login failed");
  }

  return res.json();
}

export async function fetchCurrentUser(token?: string) {
  const authToken = token || getToken();
  const res = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });

  if (!res.ok) throw new Error("Failed to load user profile");
  return res.json();
}

// ============ Content ============

export async function getLibrary() {
  return authFetch(`${API_URL}/content/library`);
}

export async function getContent(contentId: number) {
  return authFetch(`${API_URL}/content/${contentId}`);
}

export async function uploadContent(formData: FormData) {
  const token = getToken();
  const res = await fetch(`${API_URL}/content/`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Upload failed");
  }

  return res.json();
}

export async function addYouTubeContent(url: string, title: string) {
  return authFetch(`${API_URL}/content/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_type: "youtube", source_url: url, title }),
  });
}

export async function deleteContent(contentId: number) {
  const token = getToken();
  await fetch(`${API_URL}/content/${contentId}`, {
    method: "DELETE",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

export async function completeChunk(
  contentId: number,
  chunkId: number,
  data: { quiz_score: number; average_attention: number; time_spent_seconds: number }
) {
  return authFetch(`${API_URL}/content/${contentId}/chunks/${chunkId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

// ============ Gamification ============

export async function getGamificationStats(): Promise<GamificationStats> {
  return authFetch(`${API_URL}/gamification/user/coins`);
}

export async function freezeStreak() {
  return authFetch(`${API_URL}/gamification/user/streak/freeze`, { method: "POST" });
}

export async function getMilestones() {
  return authFetch(`${API_URL}/gamification/user/milestones`);
}

export async function getShopItems(): Promise<{ items: ShopItem[]; user_balance: number }> {
  return authFetch(`${API_URL}/gamification/shop/items`);
}

export async function purchaseItem(itemId: string) {
  return authFetch(`${API_URL}/gamification/shop/purchase/${itemId}`, { method: "POST" });
}

export async function getInventory() {
  return authFetch(`${API_URL}/gamification/user/inventory`);
}

export async function equipItem(inventoryId: number) {
  return authFetch(`${API_URL}/gamification/user/inventory/${inventoryId}/equip`, { method: "POST" });
}

export async function getLeaderboard() {
  return authFetch(`${API_URL}/gamification/leaderboard`);
}

// ============ ADHD Learning ============

export async function getFocusRecovery(contentId: number) {
  return authFetch(`${API_URL}/adhd-learning/content/${contentId}/recovery`);
}

export async function getSmartTimestamps(contentId: number) {
  return authFetch(`${API_URL}/adhd-learning/content/${contentId}/timestamps`);
}

export async function reportAttentionLoss(data: {
  content_id: number;
  chunk_id: number;
  attention_level: number;
  time_distracted_seconds: number;
  session_duration_seconds: number;
}) {
  return authFetch(`${API_URL}/adhd-learning/session/attention-alert`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getDifficultyRecommendation() {
  return authFetch(`${API_URL}/adhd-learning/user/difficulty-recommendation`);
}

export async function getProgressiveContent(contentId: number, chunkId: number) {
  return authFetch(`${API_URL}/adhd-learning/content/${contentId}/progressive-disclosure?chunk_id=${chunkId}`);
}

// ============ Analytics ============

export async function getUserProgress() {
  return authFetch(`${API_URL}/analytics/progress`);
}

export async function getContentAnalytics(contentId: number) {
  return authFetch(`${API_URL}/analytics/content/${contentId}`);
}

export async function getADHDInsights() {
  return authFetch(`${API_URL}/analytics/adhd-insights`);
}
