'use client'

import { useState, useEffect } from 'react'
import { User, Bot } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

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

// Preprocess content to format dashes as proper markdown lists
function formatContentForMarkdown(content) {
  if (!content) return content
  
  let result = content
  
  // First, handle inline dashes that should be list items
  // Pattern: " - " or ": - " followed by text that looks like a list item header
  // This handles cases like "summary: - Item 1: text - Item 2: text"
  // Match: " - " or ": - " followed by capitalized words ending with ":"
  result = result.replace(/([^\n]) - ([A-Z][^:]+:)/g, '$1\n\n- $2')
  
  // Also handle cases where there's a colon before the dash
  result = result.replace(/(:\s+) - ([A-Z][^:]+:)/g, '$1\n\n- $2')
  
  // Now split by lines and ensure proper spacing for list items
  let lines = result.split('\n')
  let formattedLines = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    
    // Check if this line starts with a dash (potential list item)
    if (trimmed.match(/^[-•]\s+/)) {
      // If previous line exists and isn't empty and isn't already a list item, add blank line
      if (i > 0 && formattedLines.length > 0) {
        const prevLine = formattedLines[formattedLines.length - 1]
        const prevTrimmed = prevLine.trim()
        // Only add blank line if previous line isn't empty and isn't a list item
        if (prevTrimmed && !prevTrimmed.match(/^[-•]\s+/)) {
          formattedLines.push('')
        }
      }
      formattedLines.push(line)
    } else {
      formattedLines.push(line)
    }
  }
  
  return formattedLines.join('\n')
}

export default function MessageBubble({ message }) {
  const { sender, content, timestamp, agentType, isStreaming } = message
  const agentInfo = getAgentInfo(agentType)
  
  // Format content synchronously to avoid hydration mismatch
  const formattedContent = content ? formatContentForMarkdown(content) : ''
  
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
          <div className="text-sm leading-relaxed prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{formattedContent || content}</ReactMarkdown>
          </div>
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
        <div className="text-sm leading-relaxed prose prose-sm max-w-none">
          <ReactMarkdown
            components={{
              // Custom styling for markdown elements
              p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
              ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
              ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
              li: ({node, ...props}) => <li className="ml-2" {...props} />,
              strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
              em: ({node, ...props}) => <em className="italic" {...props} />,
              code: ({node, ...props}) => <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono" {...props} />,
              h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-2 mt-3 first:mt-0" {...props} />,
              h2: ({node, ...props}) => <h2 className="text-base font-bold mb-2 mt-3 first:mt-0" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-sm font-bold mb-2 mt-3 first:mt-0" {...props} />,
            }}
          >
            {formattedContent || content}
          </ReactMarkdown>
          {isStreaming && <span className="animate-pulse inline-block ml-1">|</span>}
        </div>
        <p className="text-xs mt-3 text-gray-500">{displayTimestamp}</p>
      </div>
    </div>
  )
}

