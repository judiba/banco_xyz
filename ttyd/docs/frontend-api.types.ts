/**
 * Tipos da API v1 TTYD — copiar para o projeto Angular:
 *   src/app/core/api/api.types.ts
 *
 * OpenAPI (geração automática): http://localhost:8000/openapi.json
 */

export interface ApiErrorDetail {
  field?: string;
  message: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: ApiErrorDetail[];
    requestId: string;
  };
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: 'Bearer';
}

export interface User {
  id: string;
  username: string;
  displayName: string;
  email: string | null;
  roles: string[];
  tenantId: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  tokens: AuthTokens;
  user: User;
}

export interface RefreshRequest {
  refreshToken: string;
}

export interface RefreshResponse {
  tokens: AuthTokens;
}

export interface LogoutRequest {
  refreshToken?: string;
}

export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

export interface ConversationSummary {
  id: string;
  title: string;
  description: string | null;
  lastUpdatedAt: number;
  folderId: string | null;
}

export interface CreateConversationRequest {
  title?: string;
  folderId?: string | null;
}

export interface PatchConversationRequest {
  title?: string;
  folderId?: string | null;
}

export type MessageRole = 'user' | 'assistant';
export type MessageFeedback = 'like' | 'dislike' | null;

export interface ChatMessage {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  createdAt: number;
  status?: 'pending' | 'completed' | 'failed';
  feedback?: MessageFeedback;
}

export interface SendMessageRequest {
  content: string;
}

export interface SendMessageResponse {
  conversation: ConversationSummary;
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
}

export interface WithMessageRequest {
  content: string;
  folderId?: string | null;
}

export interface WithMessageResponse {
  conversation: ConversationSummary;
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
}

export interface Folder {
  id: string;
  name: string;
  slug: string;
  createdAt?: number;
  updatedAt?: number;
  conversationsCount?: number;
}

export interface FoldersListResponse {
  data: Folder[];
}

export interface CreateFolderRequest {
  name: string;
}

export interface PatchFolderRequest {
  name: string;
}

export interface BootstrapResponse {
  user: User;
  conversations: PaginatedResponse<ConversationSummary>;
  folders: FoldersListResponse;
  assistant: { displayName: string };
}

export interface FeedbackRequest {
  feedback: 'like' | 'dislike' | null;
}

export interface FeedbackResponse {
  messageId: string;
  feedback: MessageFeedback;
  updatedAt: number;
}

export interface RegenerateRequest {
  instruction?: string;
}

export interface RegenerateResponse {
  message: ChatMessage;
  conversation: ConversationSummary;
}

export type SseEventType =
  | 'user_message'
  | 'assistant_start'
  | 'assistant_delta'
  | 'assistant_done'
  | 'conversation_updated'
  | 'error';

export interface SseUserMessagePayload {
  message: ChatMessage;
}

export interface SseAssistantStartPayload {
  messageId: string;
  conversationId: string;
}

export interface SseAssistantDeltaPayload {
  messageId: string;
  delta: string;
}

export interface SseAssistantDonePayload {
  message: ChatMessage;
}

export interface SseConversationUpdatedPayload {
  conversation: ConversationSummary;
}

export interface SseErrorPayload {
  code: string;
  message: string;
}

/** Códigos de erro conhecidos — alinhar com handleApiError no front */
export type ApiErrorCode =
  | 'AUTH_INVALID_CREDENTIALS'
  | 'AUTH_TOKEN_EXPIRED'
  | 'CONVERSATION_NOT_FOUND'
  | 'FOLDER_NOT_FOUND'
  | 'FOLDER_DUPLICATE_NAME'
  | 'VALIDATION_ERROR'
  | 'CHAT_RATE_LIMIT'
  | 'LLM_UNAVAILABLE'
  | 'NOT_IMPLEMENTED'
  | 'NOT_FOUND'
  | 'INTERNAL_ERROR';
