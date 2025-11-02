'use client'

import { useState, useEffect } from 'react'
import { User, Bot } from 'lucide-react'

const getAgentInfo = (agentType) => {
  const agents = {
    policy: { 
      name: 'Policy Specialist', 
      color: 'bg-gradient-to-r from-blue-500 to-cyan-500', 
      icon: '📋', 
      badge: 'POLICY',
      bgColor: 'bg-gradient-to-r from-blue-100 to-cyan-100',
      borderColor: 'border-blue-300'
    },
    technical: { 
      name: 'Technical Support', 
      color: 'bg-gradient-to-r from-green-500 to-emerald-500', 
      icon: '🔧', 
      badge: 'TECHNICAL',
      bgColor: 'bg-gradient-to-r from-green-100 to-emerald-100',
      borderColor: 'border-green-300'
    },
    billing: { 
      name: 'Billing Support', 
      color: 'bg-gradient-to-r from-purple-500 to-pink-500', 
      icon: '💳', 
      badge: 'BILLING',
      bgColor: 'bg-gradient-to-r from-purple-100 to-pink-100',
      borderColor: 'border-purple-300'
    },
    dad_joke: { 
      name: 'ESDJ Bot', 
      color: 'bg-gradient-to-r from-pink-500 to-rose-500', 
      icon: '🤣', 
      badge: 'DAD JOKE',
      bgColor: 'bg-gradient-to-r from-pink-100 to-rose-100',
      borderColor: 'border-pink-300'
    },
    support: { 
      name: 'Workplace Specialist', 
      color: 'bg-gradient-to-r from-cyan-500 to-blue-500', 
      icon: '🏢', 
      badge: 'SUPPORT',
      bgColor: 'bg-white',
      borderColor: 'border-cyan-200'
    }
  }
  return agents[agentType] || agents.support
}

export default function MessageBubble({ message }) {
  const { sender, content, timestamp, agentType, isStreaming } = message
  const agentInfo = getAgentInfo(agentType)
  const [displayTimestamp, setDisplayTimestamp] = useState('')

  // Generate timestamp only on client to avoid hydration mismatch
  useEffect(() => {
    if (timestamp) {
      // If timestamp is already a string, use it; otherwise format it
      setDisplayTimestamp(typeof timestamp === 'string' ? timestamp : new Date(timestamp).toLocaleTimeString())
    } else {
      setDisplayTimestamp(new Date().toLocaleTimeString())
    }
  }, [timestamp])

  if (sender === 'user') {
    return (
      <div className="flex gap-3 justify-end">
        <div className="max-w-xs lg:max-w-md px-5 py-4 rounded-2xl shadow-md bg-gradient-to-r from-gray-600 to-gray-700 text-white">
          <p className="text-sm leading-relaxed whitespace-pre-line">{content}</p>
          <p className="text-xs mt-3 text-gray-300">{displayTimestamp}</p>
        </div>
        <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-600 rounded-2xl flex items-center justify-center shadow-lg">
          <User className="w-6 h-6 text-white" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3 justify-start">
      <div className="flex flex-col items-center gap-1">
        <div className={`w-12 h-12 rounded-2xl ${agentInfo.color} flex items-center justify-center text-white shadow-lg text-xl`}>
          {agentInfo.icon}
        </div>
        <div className={`text-xs px-2 py-1 rounded-full font-bold text-white shadow-sm ${agentInfo.color}`}>
          {agentInfo.badge}
        </div>
      </div>
      
      <div className={`max-w-xs lg:max-w-md px-5 py-4 rounded-2xl shadow-md ${
        agentType === 'support' 
          ? 'bg-white border-2 border-cyan-200 text-gray-900'
          : `${agentInfo.bgColor} border-2 ${agentInfo.borderColor} text-gray-900`
      }`}>
        <p className="text-sm leading-relaxed whitespace-pre-line">
          {content}
          {isStreaming && <span className="animate-pulse">|</span>}
        </p>
        <p className="text-xs mt-3 text-gray-500">{displayTimestamp}</p>
      </div>
    </div>
  )
}

