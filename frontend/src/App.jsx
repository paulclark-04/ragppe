import React, { useState } from 'react';
import { UploadZone } from './components/UploadZone';
import { SummaryView } from './components/SummaryView';
import { Sparkles } from 'lucide-react';

function App() {
  const [uploadResult, setUploadResult] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg text-white">
              <Sparkles size={20} />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              MultiSummarizer
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!uploadResult ? (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Transform Content into Knowledge
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                Upload PDF documents, audio recordings, or videos. Our AI will analyze, summarize, and answer your questions instantly.
              </p>
            </div>
            <UploadZone onUploadComplete={setUploadResult} />
          </div>
        ) : (
          <div className="space-y-6">
            <button
              onClick={() => setUploadResult(null)}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              ← Upload another file
            </button>
            <SummaryView
              summary={uploadResult.preview}
              filename={uploadResult.filename}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
