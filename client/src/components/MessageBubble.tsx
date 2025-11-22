import React from 'react';
import { Role, Message } from '@/types';
import { FileText, Bot, Share2, MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === Role.USER;

  const formatTime = (date: Date) => {
    return date.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-8">
        <div className="bg-gray-200 text-slate-800 rounded-2xl rounded-tr-none px-6 py-4 max-w-[80%] md:max-w-[60%] shadow-sm">
          <div className="flex items-center gap-2 mb-1 opacity-70">
            <span className="font-semibold text-xs uppercase tracking-wider text-gray-600">User</span>
          </div>
          <p className="text-md leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 mb-8 max-w-[95%]">
      <div className="flex-shrink-0 mt-1">
        <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-white shadow-md">
          <Bot size={20} />
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-3 mb-1">
          <span className="font-bold text-slate-900">CivicFlow Assistant</span>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-0 overflow-hidden">
          {/* Header/Context Bar inside bubble similar to screenshot */}
          <div className="bg-slate-800 text-white px-4 py-2 text-xs font-medium flex justify-between items-center">
            <span>Response to your query</span>
            <span className="opacity-60">{formatTime(message.timestamp)}</span>
          </div>

          <div className="p-5">
            {message.isThinking ? (
              <div className="flex items-center gap-2 text-gray-500 animate-pulse">
                <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                <div className="w-2 h-2 bg-teal-500 rounded-full delay-75"></div>
                <div className="w-2 h-2 bg-teal-500 rounded-full delay-150"></div>
                <span className="text-sm">Analyzing city documents...</span>
              </div>
            ) : (
              <div className="text-slate-700 leading-relaxed space-y-4">
                <p>{message.content}</p>
              </div>
            )}

            {/* Sources & Citations Section */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-100">
                <h4 className="text-sm font-bold text-slate-900 mb-3">Sources & Citations:</h4>
                <div className="space-y-2">
                  {message.citations.map((citation) => (
                    <a
                      key={citation.id}
                      href={citation.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-2 rounded-md bg-teal-50 border border-teal-100 hover:bg-teal-100 transition-colors group"
                    >
                      <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded bg-teal-600 text-white text-xs font-bold">
                        {citation.id}
                      </span>
                      <FileText size={16} className="text-teal-700" />
                      <span className="text-sm font-medium text-teal-900 truncate underline-offset-2 group-hover:underline">
                        {citation.title}
                      </span>
                      {citation.type && (
                        <span className="ml-auto text-xs text-teal-600 font-medium px-2 py-0.5 bg-white rounded-full border border-teal-100">
                          {citation.type} {citation.size ? `, ${citation.size}` : ''}
                        </span>
                      )}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {!message.isThinking && (
            <div className="bg-gray-50 px-5 py-3 flex justify-end gap-2 border-t border-gray-100">
              <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                <Share2 size={14} />
                Share Answer
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                <MessageSquare size={14} />
                Provide Feedback
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};