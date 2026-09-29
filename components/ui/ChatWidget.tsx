'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { sendChatMessage, ChatResult } from '@/lib/api/endpoints';
import { getOrCreateSession } from '@/lib/api/user';
import ContentCard from '@/components/ui/ContentCard';

interface Message {
    id: string;
    role: 'user' | 'ai';
    content: string;
    results?: ChatResult[];
}

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'init',
            role: 'ai',
            content: "Hi! I'm your MAVILON AI assistant. Tell me what kind of mood you're in, or give me a prompt like 'show me a dark sci-fi movie with a twist'."
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim() || isTyping) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const sessionId = await getOrCreateSession();
            const response = await sendChatMessage(userMsg.content, sessionId, 3);

            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'ai',
                content: response.response,
                results: response.results
            };

            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'ai',
                content: "AI assistant temporarily unavailable."
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute bottom-16 right-0 w-80 sm:w-96 h-[32rem] max-h-[80vh] bg-dark-800 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden glass-strong"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-dark-900/50">
                            <div className="flex items-center gap-2">
                                <Bot className="w-5 h-5 text-neon-cyan" />
                                <h3 className="font-bold text-white">MAVILON AI</h3>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-gray-400 hover:text-white transition-colors p-1"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
                            {messages.map(msg => (
                                <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`
                                        max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed
                                        ${msg.role === 'user'
                                            ? 'bg-neon-cyan text-black rounded-tr-sm'
                                            : 'bg-white/10 text-gray-200 rounded-tl-sm border border-white/5'}
                                    `}>
                                        {msg.content}
                                    </div>

                                    {/* AI Results Carousel */}
                                    {msg.results && msg.results.length > 0 && (
                                        <div className="mt-3 w-full flex gap-3 overflow-x-auto pb-2 scrollbar-hide snap-x">
                                            {msg.results.map((result, idx) => (
                                                <div key={idx} className="shrink-0 w-32 snap-start">
                                                    <ContentCard content={result.content} explanation={result.explanation} />
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}

                            {isTyping && (
                                <div className="flex items-start">
                                    <div className="bg-white/10 border border-white/5 p-3 rounded-2xl rounded-tl-sm text-gray-400 flex items-center gap-2">
                                        <Loader2 className="w-4 h-4 animate-spin text-neon-cyan" />
                                        <span className="text-xs">Thinking...</span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-3 bg-dark-900/80 border-t border-white/10">
                            <form
                                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                                className="flex gap-2 relative"
                            >
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Ask for a recommendation..."
                                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-neon-cyan placeholder:text-gray-500 transition-colors"
                                    disabled={isTyping}
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim() || isTyping}
                                    className="absolute right-1 top-1 bottom-1 aspect-square bg-neon-cyan text-black rounded-lg flex items-center justify-center disabled:opacity-50 transition-colors hover:bg-cyan-400"
                                >
                                    <Send className="w-4 h-4 ml-0.5" />
                                </button>
                            </form>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Bubble Button */}
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-colors
                    ${isOpen ? 'bg-dark-800 text-white border border-white/20' : 'bg-neon-cyan text-black shadow-glow-cyan'}
                `}
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
            </motion.button>
        </div>
    );
}
