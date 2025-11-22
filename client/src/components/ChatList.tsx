import React, { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { Message } from '@/types';

interface ChatListProps {
  messages: Message[];
}

export const ChatList: React.FC<ChatListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <main className="flex-1 overflow-y-auto scroll-smooth custom-scrollbar">
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">
        
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        <div ref={messagesEndRef} />
      </div>
    </main>
  );
};
