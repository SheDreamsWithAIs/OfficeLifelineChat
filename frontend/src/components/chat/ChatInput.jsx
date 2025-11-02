'use client'

import { Send, Loader2 } from 'lucide-react'
import { useState, useEffect } from 'react'

const suggestionQuestions = [
  "Help with my workload",
  "Please summarize the privacy policy",
  "How do I fix API errors?",
  "What are your pricing plans?"
]

export default function ChatInput({ inputMessage, setInputMessage, isLoading, onSendMessage }) {
  const [currentSuggestion, setCurrentSuggestion] = useState(0)

  // Rotate suggestion every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSuggestion(prev => (prev + 1) % suggestionQuestions.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage)
    }
  }

  return (
    <>
      {/* Single Rotating Suggestion (when minimal messages) */}
      <div className="px-4 pb-4">
        <div className="text-center">
          <div className="max-w-sm mx-auto">
            <div className="p-4 text-sm text-gray-600 bg-gradient-to-r from-cyan-50 via-purple-50 to-pink-50 rounded-xl border-2 border-purple-200 shadow-sm">
              <span className="text-purple-500 font-semibold">💡 Try asking: </span>
              <span className="italic">"{suggestionQuestions[currentSuggestion]}"</span>
            </div>
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t-2 border-purple-200 p-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="What's your office crisis today? 🏢"
              disabled={isLoading}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              className="flex-1 p-4 border-2 border-purple-300 rounded-xl focus:ring-4 focus:ring-cyan-200 focus:border-cyan-400 disabled:bg-gray-100 placeholder-gray-500 text-gray-900"
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-4 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 text-white rounded-xl hover:from-cyan-600 hover:via-purple-600 hover:to-pink-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition shadow-lg hover:shadow-xl flex items-center gap-2 font-bold"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <div className="mt-3 text-xs text-gray-500 text-center">
            💼 Press Enter to submit • Our AI agent is ready to help! 😄
          </div>
        </div>
      </div>
    </>
  )
}

