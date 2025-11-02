'use client'

import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import Sidebar from '../sidebar/Sidebar'

const WELCOME_MESSAGE = {
  id: 1,
  content: "Welcome to OfficeLifeline! 🏢 Where we solve workplace problems with a healthy dose of sarcasm and questionable life choices! I'm your AI support specialist, and fair warning: I come with a built-in dad joke dispenser and zero corporate filter! How can I help you navigate the beautiful chaos of office life today?",
  sender: 'ai',
  timestamp: Date.now(),
  agentType: 'support'
}

export default function ChatInterface() {
  // Load messages and thread_id from localStorage on mount
  const [messages, setMessages] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('chat_messages')
      if (saved) {
        try {
          return JSON.parse(saved)
        } catch (e) {
          console.error('Failed to parse saved messages:', e)
        }
      }
    }
    return [WELCOME_MESSAGE]
  })
  
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  // Load thread_id from localStorage or initialize as null
  const [currentThreadId, setCurrentThreadId] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('chat_thread_id') || null
    }
    return null
  })

  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingMessage])

  // Save thread_id to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (currentThreadId) {
        localStorage.setItem('chat_thread_id', currentThreadId)
      } else {
        localStorage.removeItem('chat_thread_id')
      }
    }
  }, [currentThreadId])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chat_messages', JSON.stringify(messages))
    }
  }, [messages])

  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      content: message,
      sender: 'user',
      timestamp: Date.now() // Use timestamp number, formatted client-side
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setStreamingMessage('')

    // Generate thread ID if not exists
    const threadId = currentThreadId || `user_${Date.now()}_1`
    if (!currentThreadId) {
      setCurrentThreadId(threadId)
    }

    // Import streaming function dynamically
    const { streamChatMessage } = await import('../../lib/api')
    
    let fullResponse = ''
    let agentType = 'support'

    streamChatMessage(
      message,
      threadId,
      (chunk) => {
        fullResponse += chunk.content || ''
        agentType = chunk.agent_type || agentType
        setStreamingMessage(fullResponse)
      },
      () => {
        const aiResponse = {
          id: Date.now() + 1,
          content: fullResponse,
          sender: 'ai',
          timestamp: Date.now(), // Use timestamp number, formatted client-side
          agentType: agentType
        }
        setMessages(prev => [...prev, aiResponse])
        setStreamingMessage('')
        setIsLoading(false)
      },
      (error) => {
        console.error('Streaming error:', error)
        const errorMessage = {
          id: Date.now() + 1,
          content: 'Sorry, I encountered an error. Please try again.',
          sender: 'ai',
          timestamp: Date.now(), // Use timestamp number, formatted client-side
          agentType: 'support'
        }
        setMessages(prev => [...prev, errorMessage])
        setStreamingMessage('')
        setIsLoading(false)
      }
    )
  }

  const clearChat = () => {
    // Reset to welcome message
    const welcomeMsg = {
      ...WELCOME_MESSAGE,
      timestamp: Date.now() // Update timestamp for new session
    }
    setMessages([welcomeMsg])
    
    // Clear thread_id from state and localStorage to start fresh conversation
    // This ensures backend starts a new thread on next message
    setCurrentThreadId(null)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('chat_thread_id')
      localStorage.setItem('chat_messages', JSON.stringify([welcomeMsg]))
    }
  }

  return (
    <div className="h-screen bg-gradient-to-br from-cyan-50 via-pink-50 to-purple-50 flex">
      <Sidebar 
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        clearChat={clearChat}
        onSuggestionClick={handleSendMessage}
      />
      
      <div className="flex-1 flex flex-col">
        <MessageList 
          messages={messages}
          streamingMessage={streamingMessage}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
          onMenuClick={() => setSidebarOpen(true)}
          onClearChat={clearChat}
        />
        
        <ChatInput
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  )
}

