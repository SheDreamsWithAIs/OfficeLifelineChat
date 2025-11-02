'use client'

import { useState, useEffect } from 'react'
import { X, RotateCcw, HelpCircle, Settings, Briefcase, Zap } from 'lucide-react'

const companyMottos = [
  "Turning workplace drama into workplace dharma! 🧘‍♀️",
  "We put the 'fun' in 'fundamentally broken corporate systems'! 🎉",
  "Because every office needs a reality check and a dad joke! ⚡",
  "Solving problems one eye-roll at a time! 👀"
]

const suggestionQuestions = [
  "Please tell me a joke",
  "Tell me about privacy policy",
  "How do I fix API errors?",
  "What are your pricing plans?"
]

export default function Sidebar({ sidebarOpen, setSidebarOpen, clearChat, onSuggestionClick }) {
  const [randomMotto, setRandomMotto] = useState(companyMottos[0])

  // Generate random motto only on client side to avoid hydration mismatch
  useEffect(() => {
    setRandomMotto(companyMottos[Math.floor(Math.random() * companyMottos.length)])
  }, [])

  return (
    <>
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-2xl transform transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-lg">
              <Briefcase className="w-7 h-7 text-cyan-600" />
            </div>
            <div>
              <h1 className="font-black text-white text-xl">OfficeLifeline</h1>
              <p className="text-xs text-cyan-100 font-medium">Workplace Problems • Meet Solutions</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-white/20 text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-purple-500" />
              Today's Office Wisdom
            </h3>
            <div className="p-4 bg-gradient-to-r from-cyan-100 via-purple-100 to-pink-100 rounded-xl border-l-4 border-cyan-500">
              <p className="text-sm text-gray-700 font-medium">
                {randomMotto}
              </p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-800 mb-3">Quick Escape Routes</h3>
            <div className="space-y-2">
              <button
                onClick={clearChat}
                className="w-full flex items-center gap-3 p-3 text-sm text-gray-700 hover:bg-gradient-to-r hover:from-cyan-50 hover:to-purple-50 rounded-lg transition border-2 border-cyan-200 hover:border-purple-300 font-semibold"
              >
                <RotateCcw className="w-4 h-4" />
                Start a New Chat
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-sm text-gray-700 hover:bg-gradient-to-r hover:from-pink-50 hover:to-purple-50 rounded-lg transition border-2 border-pink-200 hover:border-purple-300">
                <HelpCircle className="w-4 h-4" />
                Office Survival Guide
              </button>
              <button className="w-full flex items-center gap-3 p-3 text-sm text-gray-700 hover:bg-gradient-to-r hover:from-purple-50 hover:to-cyan-50 rounded-lg transition border-2 border-purple-200 hover:border-cyan-300">
                <Settings className="w-4 h-4" />
                Reality Check Settings
              </button>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-800 mb-3">Try These Office Dilemmas!</h3>
            <div className="space-y-2">
              {suggestionQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => onSuggestionClick(question)}
                  className="w-full text-left p-3 text-xs text-gray-600 hover:bg-gradient-to-r hover:from-cyan-50 hover:to-pink-50 rounded-lg transition border border-gray-200 hover:border-purple-300"
                >
                  💼 "{question}"
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </>
  )
}

