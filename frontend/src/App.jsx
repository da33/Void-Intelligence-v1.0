import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Loader2, CheckCircle2, Calendar, FileText, Briefcase, Clock, StickyNote, Sparkles, X, Type } from 'lucide-react';
import { uploadAudio, submitText } from './services/api';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState('note'); // 'meeting', 'schedule', 'note'
  const [hoverMode, setHoverMode] = useState(null); // For orb morphing preview
  const [showTextModal, setShowTextModal] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [textMode, setTextMode] = useState('auto');

  // Dynamic Orb Variants based on Mode
  const orbVariants = {
    idle: { scale: 1, rotate: 0, borderRadius: "50%", backgroundColor: "#3b82f6", boxShadow: "0 0 60px #3b82f6aa" },
    hover_meeting: { scale: 1.1, rotate: 45, borderRadius: "20%", backgroundColor: "#3b82f6", boxShadow: "0 0 80px #3b82f6" },
    hover_schedule: { scale: 1.1, rotate: 180, borderRadius: "50%", backgroundColor: "#10b981", boxShadow: "0 0 80px #10b981", border: "4px solid #fff" },
    hover_note: { scale: 1.1, rotate: -15, borderRadius: "30% 70% 70% 30% / 30% 30% 70% 70%", backgroundColor: "#ec4899", boxShadow: "0 0 80px #ec4899" },
    recording: {
      scale: [1, 1.15, 1],
      borderRadius: ["50%", "45%", "50%"],
      backgroundColor: ["#3b82f6", "#ef4444", "#3b82f6"],
      boxShadow: ["0 0 60px #3b82f6", "0 0 100px #ef4444", "0 0 60px #3b82f6"],
      transition: { repeat: Infinity, duration: 2, ease: "easeInOut" }
    },
    success: {
      scale: 1.2,
      backgroundColor: "#10b981",
      boxShadow: "0 0 100px #10b981",
      borderRadius: "50%",
      transition: { duration: 0.5 }
    }
  };

  // Wake Lock Ref
  const wakeLockRef = React.useRef(null);

  const startRecording = async (selectedMode) => {
    setMode(selectedMode);
    try {
      // 1. Request Wake Lock (Keep Screen On)
      if ('wakeLock' in navigator) {
        try {
          wakeLockRef.current = await navigator.wakeLock.request('screen');
          console.log('Screen Wake Lock acquired');
        } catch (err) {
          console.error(`Wake Lock error: ${err.name}, ${err.message}`);
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        // Release Wake Lock
        if (wakeLockRef.current) {
          await wakeLockRef.current.release();
          wakeLockRef.current = null;
          console.log('Screen Wake Lock released');
        }

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

      // Auto-alert removed in favor of UI card visualization, but keeping log
      console.log('Upload Result:', data);

    } catch (error) {
      console.error("Upload error:", error);
      const url = error.config?.url || "Unknown URL";
      const status = error.response?.status || "Unknown Status";
      alert(`處理失敗 (Status: ${status})\n連線目標: ${url}\n\n錯誤訊息: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim()) {
      alert('請輸入文字內容');
      return;
    }

    setShowTextModal(false);
    setIsProcessing(true);

    try {
      const data = await submitText(textInput, textMode);
      setResult(data);
      setTextInput('');
      console.log('Text submission result:', data);
    } catch (error) {
      console.error('Text submission error:', error);
      const url = error.config?.url || 'Unknown URL';
      const status = error.response?.status || 'Unknown Status';
      alert(`處理失敗 (Status: ${status})\n連線目標: ${url}\n\n錯誤訊息: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const openTextModal = (selectedMode) => {
    setTextMode('auto');
    setShowTextModal(true);
    setResult(null);
  };

  // Reset state to initial "Idle" mode
  const resetState = () => {
    setResult(null);
    setHoverMode(null);
  };

  return (
    <div className="min-h-screen bg-void text-gray-200 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans selection:bg-primary/30">

      {/* Background Ambience & Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-900/20 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <Particles count={20} />
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
                animate={result ? "success" : (hoverMode ? `hover_${hoverMode}` : "idle")}
                variants={orbVariants}
              >
                <div className="w-32 h-32 flex items-center justify-center text-white/90">
                  {result ? <CheckCircle2 size={50} className="text-white drop-shadow-md" /> : (
                    <>
                      {hoverMode === 'meeting' && <Briefcase size={40} />}
                      {hoverMode === 'schedule' && <Clock size={40} />}
                      {hoverMode === 'note' && <StickyNote size={40} />}
                      {!hoverMode && <Mic size={40} />}
                    </>
                  )}
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

          {/* Mode Selectors (Satellites) - ONLY show when idle and NO result */}
          {!isRecording && !isProcessing && !result && (
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
          {result && <p className="text-green-400 font-mono text-sm tracking-widest">COMPLETE</p>}
        </div>

        {/* Results Card */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 40, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: 40, filter: 'blur(10px)' }}
              className="w-full mt-8 bg-glass backdrop-blur-3xl border border-white/10 rounded-2xl p-6 shadow-2xl relative"
            >
              {/* Close Button */}
              <button
                onClick={resetState}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                title="恢復 (Restore)"
              >
                <X size={20} />
              </button>

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
                {result.auto_event_link && (
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono">
                    <Calendar size={12} />
                    <span>行事曆已建立</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Text Input Button - Show when idle and no result */}
        {!isRecording && !isProcessing && !result && (
          <motion.button
            onClick={() => openTextModal(mode || 'note')}
            className="mt-8 flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm font-mono text-gray-400 hover:text-white transition-all duration-300 backdrop-blur-sm"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Type size={16} />
            <span>貼上文字</span>
          </motion.button>
        )}

      </main>

      {/* Text Input Modal */}
      <AnimatePresence>
        {showTextModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-6"
            onClick={() => setShowTextModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-void border border-white/20 rounded-2xl p-8 max-w-2xl w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Type size={24} />
                  貼上文字記事
                </h2>
                <button
                  onClick={() => setShowTextModal(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Mode Selector */}
              <div className="flex gap-2 mb-4">
                {['auto', 'note', 'meeting', 'schedule'].map((m) => (
                  <button
                    key={m}
                    onClick={() => setTextMode(m)}
                    className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${textMode === m
                      ? 'bg-primary text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                  >
                    {m === 'auto' && '自動識別'}
                    {m === 'note' && '記事'}
                    {m === 'meeting' && '會議'}
                    {m === 'schedule' && '行程'}
                  </button>
                ))}
              </div>

              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="在此貼上或輸入文字內容...\n\n例如:\n- 會議記錄\n- 待辦事項\n- 靈感筆記\n- 行程安排"
                className="w-full h-64 bg-white/5 border border-white/10 rounded-xl p-4 text-gray-200 placeholder-gray-600 focus:outline-none focus:border-primary/50 transition-colors resize-none font-mono text-sm"
                autoFocus
              />

              <div className="flex items-center justify-between mt-6">
                <span className="text-xs text-gray-500 font-mono">
                  {textInput.length} / 10000 字元
                </span>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowTextModal(false)}
                    className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-400 hover:text-white transition-all"
                  >
                    取消
                  </button>
                  <button
                    onClick={handleTextSubmit}
                    disabled={!textInput.trim()}
                    className="px-6 py-2 bg-primary hover:bg-primary/80 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg text-sm text-white font-bold transition-all"
                  >
                    提交處理
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

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

const Particles = ({ count }) => {
  return (
    <>
      {[...Array(count)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-white/20 rounded-full"
          initial={{
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            opacity: Math.random() * 0.5 + 0.1,
          }}
          animate={{
            y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight],
            opacity: [0.1, 0.5, 0.1],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </>
  );
};

export default App;
