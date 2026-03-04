"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  MessageSquare,
  Search,
  Plus,
  Send,
  MoreHorizontal,
  ExternalLink,
  User,
  LayoutDashboard,
  Settings,
  Bell,
  ShieldCheck,
  Sparkles,
  Link2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Types
interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  sources?: string[];
  timestamp: string;
}

export default function NextLeapChatApp() {
  const [sessionId] = useState(() => `sess-${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "ai",
      content: "Hello! I am your **NextLeap Academic Advisor**. How can I help you regarding our fellowship programs today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    // Initial AI message placeholder
    const aiMsgId = (Date.now() + 1).toString();
    const aiMsg: Message = {
      id: aiMsgId,
      role: "ai",
      content: "",
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, aiMsg]);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, session_id: sessionId }),
      });

      if (!response.ok) throw new Error("Failed to connect to AI engine");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      const decoder = new TextDecoder();
      let finished = false;
      let accumulatedContent = "";

      while (!finished) {
        const { value, done } = await reader.read();
        finished = done;
        if (value) {
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.replace("data: ", "");
              if (data === "[DONE]") break;

              try {
                const parsed = JSON.parse(data);
                if (parsed.text) {
                  accumulatedContent += parsed.text;
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === aiMsgId ? { ...m, content: accumulatedContent } : m
                    )
                  );
                }
                if (parsed.sources) {
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === aiMsgId ? { ...m, sources: parsed.sources } : m
                    )
                  );
                }
              } catch (e) {
                console.error("Parse error:", e, data);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiMsgId
            ? { ...m, content: "Sorry, I encountered an error. Please check if the backend is running." }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex h-screen w-full bg-[#0A1128] text-slate-100 overflow-hidden">
      {/* 1. Far Left Sidebar - Mini Nav (as seen in screenshot top bar but vertical) */}
      <nav className="w-16 border-r border-slate-800/50 flex flex-col items-center py-6 space-y-8 bg-[#0D1530]">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/40">
          <LayoutDashboard className="text-white w-6 h-6" />
        </div>
        <div className="flex-1 flex flex-col space-y-6 text-slate-400">
          <MessageSquare className="w-6 h-6 hover:text-blue-400 cursor-pointer transition-colors" />
          <Bell className="w-6 h-6 hover:text-blue-400 cursor-pointer transition-colors" />
          <ShieldCheck className="w-6 h-6 hover:text-blue-400 cursor-pointer transition-colors" />
        </div>
        <div className="flex flex-col space-y-6 text-slate-400">
          <Settings className="w-6 h-6 hover:text-blue-400 cursor-pointer transition-colors" />
          <div className="w-8 h-8 rounded-full bg-slate-700 overflow-hidden ring-2 ring-slate-800">
            <User className="w-full h-full p-1" />
          </div>
        </div>
      </nav>

      {/* 2. Left Chat Sidebar */}
      <aside className="w-72 bg-[#121D3F] flex flex-col border-r border-slate-800/40">
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-xl font-bold tracking-tight">Chats</h1>
            <button className="p-2 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 rounded-lg transition-all">
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              placeholder="Search conversations..."
              className="w-full bg-slate-900/50 border border-slate-800/50 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-3 space-y-2 pb-6">
          <ChatListItem name="NextLeap PM advisor" lastMsg="Active now" time="09:25" active imgColor="#0066FF" />
          <ChatListItem name="Product Manager Fellowship" lastMsg="Prices updated for Cohort 48" time="10:00" imgColor="#8B5CF6" />
          <ChatListItem name="GenAI Bootcamp" lastMsg="Instructors list retrieved" time="Yesterday" imgColor="#10B981" />
          <ChatListItem name="Admission Query" lastMsg="100+ Hours Live details" time="2 days ago" imgColor="#F59E0B" />
        </div>
      </aside>

      {/* 3. Main Chat Area */}
      <section className="flex-1 flex flex-col bg-[#0A1128] relative">
        {/* Header */}
        <header className="h-20 flex items-center justify-between px-8 bg-[#0D1530]/50 backdrop-blur-md border-b border-slate-800/40 sticky top-0 z-10">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-blue-600/20 flex items-center justify-center border border-blue-500/30 ring-4 ring-blue-500/5">
              <Sparkles className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="font-semibold text-slate-100">Theron Trump</h2>
              <p className="text-xs text-slate-400 flex items-center animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                Active for support
              </p>
            </div>
          </div>
          <div className="flex space-x-3 text-slate-400">
            <button className="p-2 hover:bg-slate-800 rounded-full transition-colors"><MoreHorizontal className="w-5 h-5" /></button>
          </div>
        </header>

        {/* Dynamic Chat Messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth"
        >
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.3 }}
                className={cn(
                  "flex w-full",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                <div className={cn(
                  "flex flex-col max-w-[70%] group",
                  msg.role === "user" ? "items-end" : "items-start"
                )}>
                  {msg.role === "ai" && (
                    <span className="text-[10px] text-slate-500 mb-1 ml-4 font-medium uppercase tracking-wider">Advise Engine</span>
                  )}
                  <div className={cn(
                    "px-6 py-4 rounded-3xl text-sm leading-relaxed shadow-xl",
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-tr-none shadow-blue-900/20"
                      : "bg-[#121D3F] border border-slate-800/50 rounded-tl-none shadow-black/20"
                  )}>
                    {msg.content}
                  </div>
                  <span className="text-[10px] text-slate-500 mt-2 font-mono">{msg.timestamp}</span>
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-[#121D3F] border border-slate-800/50 px-6 py-4 rounded-3xl rounded-tl-none flex space-x-1.5 items-center">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Input Bar */}
        <div className="p-8 pb-10">
          <div className="max-w-4xl mx-auto relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition-opacity"></div>
            <div className="relative flex items-center bg-[#121D3F] border border-slate-800/50 rounded-2xl overflow-hidden focus-within:border-blue-500/50 transition-all p-2 pr-4 shadow-2xl">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type your question about NextLeap..."
                className="flex-1 bg-transparent border-none py-4 px-6 text-sm focus:outline-none placeholder:text-slate-600"
              />
              <button
                aria-label="Send query"
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="w-12 h-12 rounded-xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center shadow-lg shadow-blue-900/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Right Panel - Source Citations (as Notification panel in screenshot) */}
      <aside className="w-80 bg-[#0D1530] border-l border-slate-800/40 p-6 flex flex-col">
        <h3 className="text-slate-100 font-bold text-lg mb-6 flex items-center">
          <Link2 className="w-5 h-5 mr-3 text-blue-400" />
          Sources & Verification
        </h3>

        <div className="space-y-4">
          <p className="text-[11px] text-slate-500 font-medium uppercase tracking-[2px] mb-2">Grounding Links</p>
          {messages.filter(m => m.role === "ai" && m.sources && m.sources.length > 0).slice(-1).map((m) => (
            m.sources?.map((url, i) => (
              <div key={i} className="p-4 rounded-2xl bg-slate-900/50 border border-slate-800/50 hover:border-blue-500/30 transition-all group">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center text-blue-400">
                      <ExternalLink className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-semibold text-slate-300">Verified Citation</span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-500 truncate mb-3">{url}</p>
                <a
                  href={url} target="_blank" rel="noopener noreferrer"
                  className="text-[10px] font-bold text-blue-400 group-hover:text-blue-300 flex items-center"
                >
                  OPEN SOURCE PAGE
                  <Plus className="w-3 h-3 ml-1 transform rotate-45" />
                </a>
              </div>
            ))
          ))}
          {messages.filter(m => m.role === "ai" && m.sources && m.sources.length > 0).length === 0 && (
            <div className="text-center py-12">
              <div className="w-12 h-12 rounded-full bg-slate-800/50 mx-auto flex items-center justify-center mb-4">
                <Search className="w-6 h-6 text-slate-600" />
              </div>
              <p className="text-sm text-slate-500 italic px-8">No citations yet. Ask a question to see source verification.</p>
            </div>
          )}
        </div>

        <div className="mt-auto p-4 rounded-2xl bg-gradient-to-br from-blue-600/10 to-transparent border border-blue-600/20">
          <h4 className="text-xs font-bold text-slate-100 mb-1">Knowledge Guard</h4>
          <p className="text-[10px] text-slate-400">Strict mode enabled. All responses are derived only from vectorized NextLeap content.</p>
        </div>
      </aside>
    </main>
  );
}

function ChatListItem({ name, lastMsg, time, active, imgColor }: { name: string, lastMsg: string, time: string, active?: boolean, imgColor: string }) {
  return (
    <div className={cn(
      "flex items-center p-3 rounded-2xl cursor-pointer hover:bg-slate-800/30 transition-all",
      active ? "bg-slate-800/50 ring-1 ring-slate-700/50" : ""
    )}>
      <div
        className="w-12 h-12 rounded-2xl flex items-center justify-center mr-4"
        style={{ backgroundColor: `${imgColor}15`, border: `1px solid ${imgColor}40` }}
      >
        <User className="w-6 h-6" style={{ color: imgColor }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-center mb-1">
          <h4 className="font-semibold text-sm text-slate-100 truncate">{name}</h4>
          <span className="text-[10px] text-slate-500">{time}</span>
        </div>
        <p className="text-[11px] text-slate-500 truncate">{lastMsg}</p>
      </div>
    </div>
  );
}
