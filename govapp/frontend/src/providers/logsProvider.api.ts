import { User } from "../backend/backend.api";

export enum LogEnum {
  Email = "email",
  Phone = "phone",
  Mail = "mail",
  Person = "person",
  Other = "other"
}
export interface CommunicationLogType {
  id: number;
  label: LogEnum
}

export interface CommunicationLogDocument {
  id: number;
  name?: string;
  description?: string;
  uploadedAt: string;
  file: string;
}

export interface CommunicationLog {
  id: number;
  createdAt: string;
  type: CommunicationLogType;
  to?: string;
  cc?: string;
  from: string;
  subject?: string;
  text?: string;
  documents: Array<CommunicationLogDocument>;
  user?: User;
}
