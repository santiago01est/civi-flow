import React, { useState } from 'react';
import { ChatInput } from '../components/ChatInput';
import { ChatHeader } from '../components/ChatHeader';
import { ChatList } from '../components/ChatList';
import { FloatingActionMenu } from '../components/FloatingActionMenu';
import { Role, Message } from '@/types';

// Initial mock data to match the screenshot
const INITIAL_MESSAGES: Message[] = [
  {
    id: '1',
    role: Role.USER,
    content: "What are the current regulations on short-term rentals in Zone A?",
    timestamp: new Date('2023-08-10T17:12:00'),
  },
  {
    id: '2',
    role: Role.ASSISTANT,
    content: "According to the City's Zoning Ordinance, Chapter 17, Section 17.20.040, short-term rentals in Zone A are permitted but subject to specific operational standards and registration requirements. These regulations aim to balance tourism with neighborhood preservation.",
    timestamp: new Date('2023-08-10T17:12:05'),
    citations: [
      { id: '1', title: 'Zoning Ordinance Ch. 17, Sec. 17.20.040', uri: '#', type: 'PDF', size: '1.2 MB' },
      { id: '2', title: 'City Council Resolution No. 2023-45', uri: '#', type: 'PDF', size: '450 KB' }
    ]
  }
];

export const PolicyChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    // Placeholder for future implementation
    console.log("Sending message:", content);
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
        setIsLoading(false);
        const newMessage: Message = {
            id: Date.now().toString(),
            role: Role.USER,
            content: content,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, newMessage]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full relative">
        <ChatHeader />

        <ChatList messages={messages} />

        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />

        <FloatingActionMenu />
    </div>
  );
};
