export interface AuditFields {
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
}

export type WithAuditFields<T> = T & AuditFields;
