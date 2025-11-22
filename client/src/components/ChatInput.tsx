import React, { useState, useRef, useEffect } from 'react';
import { Mic, Paperclip, Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
      // Reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  return (
    <div className="bg-white border-t border-gray-200 p-4 md:p-6 sticky bottom-0 z-10">
      <div className="max-w-4xl mx-auto relative">
        <div className="relative flex items-end gap-2 p-2 border-2 border-teal-500 rounded-2xl bg-white shadow-sm focus-within:shadow-md transition-shadow">
          
          {/* Attachments Button */}
          <button className="p-2 text-gray-400 hover:text-teal-600 transition-colors rounded-full hover:bg-gray-100 self-end mb-1">
            <Mic size={20} />
          </button>
          <button className="p-2 text-gray-400 hover:text-teal-600 transition-colors rounded-full hover:bg-gray-100 self-end mb-1">
            <Paperclip size={20} />
            <input type="file" className="hidden" />
          </button>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about local policies, city services, or upcoming civic events..."
            className="flex-1 max-h-32 py-3 px-2 bg-transparent border-none outline-none text-slate-700 placeholder-gray-400 resize-none overflow-y-auto"
            rows={1}
            disabled={isLoading}
          />

          {/* Send Button */}
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`p-2 rounded-full mb-1 transition-all duration-200 ${
              input.trim() && !isLoading
                ? 'bg-teal-600 text-white hover:bg-teal-700 shadow-md' 
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Send size={20} className={input.trim() && !isLoading ? 'ml-0.5' : ''} />
          </button>
        </div>
        <div className="text-center mt-2">
           <p className="text-xs text-gray-400">AI can make mistakes. Please verify important information with official city documents.</p>
        </div>
      </div>
    </div>
  );
};