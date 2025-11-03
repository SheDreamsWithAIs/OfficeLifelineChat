'use client'

export default function AgentInfo() {
  return (
    <div className="bg-gradient-to-br from-purple-100 via-pink-100 to-cyan-100 p-4 rounded-xl border-2 border-purple-200">
      <h4 className="font-bold text-sm text-gray-800 mb-2 flex items-center gap-1">
        <span className="text-lg">🤖</span> AI Personalities On Duty
      </h4>
      <div className="space-y-2 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
          <span>Policy Specialist (Compliance)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          <span>Technical Support (RAG)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
          <span>Billing Support (Hybrid)</span>
        </div>
      </div>
    </div>
  )
}

