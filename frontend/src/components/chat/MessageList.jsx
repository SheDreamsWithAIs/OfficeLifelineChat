'use client'

import { Menu, Coffee } from 'lucide-react'
import MessageBubble from './MessageBubble'

export default function MessageList({ messages, streamingMessage, isLoading, messagesEndRef, onMenuClick }) {
  return (
    <>
      {/* Header */}
      <div className="bg-white border-b-2 border-purple-200 shadow-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-purple-100"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
            </div>
            <span className="font-bold text-gray-900 text-lg">OfficeLifeline Support</span>
            <span className="text-sm text-purple-600 bg-purple-100 px-3 py-1 rounded-full font-semibold">Ready to Assist</span>
          </div>
        </div>
        <div className="text-sm text-gray-500 flex items-center gap-2">
          <Coffee className="w-4 h-4" />
          Powered by LangGraph & FastAPI
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Streaming message */}
        {streamingMessage && (
          <MessageBubble 
            message={{
              id: 'streaming',
              content: streamingMessage,
              sender: 'ai',
              timestamp: Date.now(), // Use timestamp number, will be formatted client-side
              agentType: 'support',
              isStreaming: true
            }}
          />
        )}

        {/* Loading indicator */}
        {isLoading && !streamingMessage && (
          <div className="flex gap-3 justify-start">
            <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg">
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div className="max-w-xs lg:max-w-md px-5 py-4 rounded-2xl bg-white border-2 border-purple-200 shadow-md">
              <p className="text-sm text-gray-600">Consulting the office wisdom database...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </>
  )
}

