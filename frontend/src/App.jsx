import { useState } from 'react'
import EncoderTab from './components/EncoderTab'
import DecoderTab from './components/DecoderTab'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('encode')

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 w-full flex flex-col font-sans">
      <header className="bg-purple-800 text-white p-6 shadow-md w-full">
        <h1 className="text-3xl font-bold m-0 text-center">PZ-2026</h1>
      </header>
      
      <main className="flex-grow p-6 w-full flex flex-col items-center">
        <div className="flex gap-4 mb-4 w-full justify-center max-w-4xl">
          <button 
            className={`flex-1 py-3 font-semibold rounded-t-lg transition-colors text-lg ${activeTab === 'encode' ? 'bg-white text-purple-800 border-t-4 border-purple-800 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]' : 'bg-gray-200 text-gray-600 hover:bg-gray-300 border-t-4 border-transparent'}`}
            onClick={() => setActiveTab('encode')}
          >
            Encode & Hide
          </button>
          <button 
            className={`flex-1 py-3 font-semibold rounded-t-lg transition-colors text-lg ${activeTab === 'decode' ? 'bg-white text-purple-800 border-t-4 border-purple-800 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]' : 'bg-gray-200 text-gray-600 hover:bg-gray-300 border-t-4 border-transparent'}`}
            onClick={() => setActiveTab('decode')}
          >
            Extract & Decode
          </button>
        </div>

        <div className="bg-white rounded-b-lg rounded-tr-lg rounded-tl-lg shadow-lg w-full max-w-4xl overflow-hidden">
          {activeTab === 'encode' ? <EncoderTab /> : <DecoderTab />}
        </div>
      </main>
    </div>
  )
}

export default App
