import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Loader2, CheckCircle2, Calendar, FileText, Briefcase, Clock, StickyNote, Sparkles } from 'lucide-react';
import { uploadAudio } from './services/api';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState('note'); // 'meeting', 'schedule', 'note'
  const [hoverMode, setHoverMode] = useState(null); // For orb morphing preview

  // Dynamic Orb Variants based on Mode
  const orbVariants = {
    idle: { scale: 1, rotate: 0, borderRadius: "50%", backgroundColor: "#3b82f6" },
    hover_meeting: { scale: 1.1, rotate: 45, borderRadius: "20%", backgroundColor: "#3b82f6", boxShadow: "0 0 30px #3b82f6" },
    hover_schedule: { scale: 1.1, rotate: 180, borderRadius: "50%", backgroundColor: "#10b981", boxShadow: "0 0 30px #10b981", border: "4px solid #fff" },
    hover_note: { scale: 1.1, rotate: -15, borderRadius: "30% 70% 70% 30% / 30% 30% 70% 70%", backgroundColor: "#ec4899", boxShadow: "0 0 30px #ec4899" },
    recording: { scale: [1, 1.2, 1], borderRadius: ["50%", "40%", "50%"], transition: { repeat: Infinity, duration: 1.5 } }
  };

  const startRecording = async (selectedMode) => {
    setMode(selectedMode);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        const mimeType = recorder.mimeType || 'audio/webm';
        const blob = new Blob(chunks, { type: mimeType });
        console.log("Recording stopped. Blob size:", blob.size, "Type:", mimeType);
        handleUpload(blob, mimeType, selectedMode);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setResult(null);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("無法存取麥克風，請檢查權限");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleUpload = async (blob, mimeType, currentMode) => {
    setIsProcessing(true);
    try {
      let ext = 'webm';
      if (mimeType.includes('mp4')) ext = 'mp4';
      else if (mimeType.includes('ogg')) ext = 'ogg';

      const filename = `recording.${ext}`;
      console.log(`Uploading as ${filename} (${mimeType}) Mode: ${currentMode}`);

      const data = await uploadAudio(blob, filename, currentMode);
      setResult(data);
    } catch (error) {
      console.error("Upload error:", error);
      const url = error.config?.url || "Unknown URL";
      const status = error.response?.status || "Unknown Status";
      alert(`處理失敗 (Status: ${status})\n連線目標: ${url}\n\n錯誤訊息: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-void text-gray-200 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans selection:bg-primary/30">

      {/* Background Ambience */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-900/20 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      <main className="w-full max-w-lg z-10 flex flex-col items-center">

        {/* Header */}
        <header className="mb-16 text-center space-y-4">
          <h1 className="text-7xl font-extralight tracking-[0.25em] text-white/90 font-mono blur-[0.5px]">VOID</h1>
          <p className="text-gray-600 text-xs tracking-[0.5em] uppercase font-mono">Sensory Interface</p>
        </header>

        {/* The Core (Orb) */}
        <div className="relative h-64 w-64 flex items-center justify-center mb-16">
          <AnimatePresence mode="wait">
            {!isRecording && !isProcessing && (
              <motion.div
                className="relative z-20 cursor-pointer"
                initial="idle"
                animate={hoverMode ? `hover_${hoverMode}` : "idle"}
                variants={orbVariants}
              >
                <div className="w-32 h-32 flex items-center justify-center text-white/90">
                  {/* Icon changes based on hover */}
                  {hoverMode === 'meeting' && <Briefcase size={40} />}
                  {hoverMode === 'schedule' && <Clock size={40} />}
                  {hoverMode === 'note' && <StickyNote size={40} />}
                  {!hoverMode && <Mic size={40} />}
                </div>
              </motion.div>
            )}

            {isRecording && (
              <motion.div
                className="w-40 h-40 rounded-full bg-red-500/20 flex items-center justify-center border border-red-500/50 cursor-pointer"
                onClick={stopRecording}
                animate={{ scale: [1, 1.1, 1], boxShadow: ["0 0 0px #ef4444", "0 0 50px #ef4444", "0 0 0px #ef4444"] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <Square size={32} className="fill-current text-white" />
              </motion.div>
            )}

            {isProcessing && (
              <div className="relative">
                <div className="w-32 h-32 rounded-full border-2 border-white/10 border-t-primary animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Loader2 size={32} className="text-primary animate-pulse" />
                </div>
              </div>
            )}
          </AnimatePresence>

          {/* Mode Selectors (Satellites) */}
          {!isRecording && !isProcessing && (
            <>
              {/* Meeting */}
              <ModeTrigger
                mode="meeting"
                label="會議"
                color="text-neon-blue"
                position="absolute -left-12 top-10"
                setHover={() => setHoverMode('meeting')}
                onClick={() => startRecording('meeting')}
              />
              {/* Schedule */}
              <ModeTrigger
                mode="schedule"
                label="行程"
                color="text-neon-green"
                position="absolute -right-12 top-10"
                setHover={() => setHoverMode('schedule')}
                onClick={() => startRecording('schedule')}
              />
              {/* Note */}
              <ModeTrigger
                mode="note"
                label="記事"
                color="text-neon-pink"
                position="absolute bottom-[-20px]"
                setHover={() => setHoverMode('note')}
                onClick={() => startRecording('note')}
              />
            </>
          )}
        </div>

        {/* Status Text */}
        <div className="h-10 text-center">
          {isRecording && <p className="text-red-400 font-mono text-sm animate-pulse">RECORDING IN PROGRESS...</p>}
          {isProcessing && <p className="text-primary font-mono text-sm">PROCESSING DATA...</p>}
          {!isRecording && !isProcessing && !result && <p className="text-gray-600 text-sm">請選擇模式 (Select Mode)</p>}
        </div>

        {/* Results Card */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 40, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              className="w-full mt-8 bg-glass backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-secondary" />
                  <span className="text-sm font-bold text-gray-300">分析完成</span>
                </div>
                <span className="text-xs font-mono text-gray-500">{new Date().toLocaleTimeString()}</span>
              </div>

              <h3 className="text-xl font-bold text-white mb-2">{result.summary}</h3>
              <p className="text-gray-400 text-sm leading-relaxed mb-6 font-light">{result.text}</p>

              <div className="flex items-center gap-2 mt-6">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-mono">
                  <CheckCircle2 size={12} />
                  <span>SYNCED TO VOID</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </main>

      {/* Footer Branding */}
      <footer className="absolute bottom-6 text-center">
        <div className="flex flex-col items-center gap-1 opacity-20 hover:opacity-50 transition-opacity duration-500 cursor-default">
          <Sparkles size={12} className="text-white mb-1" />
          <span className="text-[10px] font-mono tracking-[0.3em] text-white">VOID PROTOCOL V1.0</span>
          <span className="text-[8px] font-mono tracking-[0.1em] text-gray-500">SYSTEM OPERATIONAL</span>
        </div>
      </footer>
    </div>
  );
}

const ModeTrigger = ({ mode, label, color, position, setHover, onClick }) => (
  <motion.button
    className={`${position} group flex flex-col items-center gap-2`}
    onHoverStart={setHover}
    onHoverEnd={() => setHover(null)}
    onClick={onClick}
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.95 }}
  >
    <div className={`w-3 h-3 rounded-full bg-white/20 group-hover:bg-current ${color} transition-colors duration-300 shadow-[0_0_10px_currentColor]`} />
    <span className={`text-xs font-bold tracking-widest uppercase text-gray-500 group-hover:text-white transition-colors`}>{label}</span>
  </motion.button>
);

export default App;
