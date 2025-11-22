import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { MessageBubble } from './components/MessageBubble';
import { ChatInput } from './components/ChatInput';
import { Role, Message, Citation } from '@/types';
import { Search, Plus, Menu, X } from 'lucide-react';

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

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('policy-chat');
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [isLoading, setIsLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div className="absolute left-0 top-0 h-full z-50" onClick={e => e.stopPropagation()}>
             <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        
        {/* Header */}
        <header className="bg-white h-16 border-b border-gray-200 flex items-center justify-between px-4 md:px-8 flex-shrink-0">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-slate-600" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
            <h1 className="text-xl font-bold text-slate-800">Policy Chat</h1>
          </div>
          
          <div className="hidden md:flex items-center relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search past conversations..." 
              className="w-full pl-10 pr-4 py-2 rounded-full bg-gray-100 border-transparent focus:bg-white focus:border-teal-500 focus:ring-2 focus:ring-teal-200 transition-all outline-none text-sm"
            />
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto scroll-smooth custom-scrollbar">
          <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">
            
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input Area */}
        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />

        {/* Floating Action Button (FAB) */}
        <button className="absolute bottom-28 right-8 w-14 h-14 bg-teal-500 hover:bg-teal-600 text-white rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-105 group z-20">
          <Plus size={28} />
          {/* Tooltip */}
          <div className="absolute right-full mr-3 bg-slate-800 text-white text-xs font-medium px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            Quick Actions & Support
          </div>
        </button>

      </div>
    </div>
  );
};

export default App;