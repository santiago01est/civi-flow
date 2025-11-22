import React from 'react';

export enum Role {
  USER = 'user',
  ASSISTANT = 'model'
}

export interface Citation {
  id: string;
  title: string;
  uri: string;
  type?: string; // PDF, Web, etc.
  size?: string;
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
  citations?: Citation[];
  isThinking?: boolean;
}

export interface NavItem {
  label: string;
  icon: React.ElementType;
  id: string;
  path?: string;
}