'use client'

import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import Sidebar from '../sidebar/Sidebar'

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Welcome to OfficeLifeline! 🏢 Where we solve workplace problems with a healthy dose of sarcasm and questionable life choices! I'm your AI support specialist, and fair warning: I come with a built-in dad joke dispenser and zero corporate filter! How can I help you navigate the beautiful chaos of office life today?",
      sender: 'ai',
      timestamp: Date.now(), // Use timestamp number, formatted client-side
      agentType: 'support'
    }
  ])
  
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentThreadId, setCurrentThreadId] = useState(null)

  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingMessage])

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
    setMessages([{
      id: 1,
      content: "Welcome to OfficeLifeline! 🏢 Where we solve workplace problems with a healthy dose of sarcasm and questionable life choices! I'm your AI support specialist, and fair warning: I come with a built-in dad joke dispenser and zero corporate filter! How can I help you navigate the beautiful chaos of office life today?",
      sender: 'ai',
      timestamp: Date.now(), // Use timestamp number, formatted client-side
      agentType: 'support'
    }])
    setCurrentThreadId(null)
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

