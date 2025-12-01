import React, { useState, useEffect } from 'react';
import { ExternalLink } from 'lucide-react';

const Header = () => {
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <header
            className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${isScrolled
                    ? 'bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-100 py-3'
                    : 'bg-transparent py-5'
                }`}
        >
            <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-xl font-semibold tracking-tight text-slate-900">
                        Overwatch <span className="text-emerald-600">Meta</span>Analyzer
                    </span>
                </div>

                <a
                    href="https://overwatch.blizzard.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-emerald-600 transition-colors"
                >
                    Links Oficiais
                    <ExternalLink size={14} />
                </a>
            </div>
        </header>
    );
};

export default Header;
