import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

const Dropdown = ({ label, items, onSelect, className = "", variant = "standard" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Estilos baseados na variante
    const buttonStyles = variant === "text"
        ? "inline-flex items-center font-bold text-slate-900 border-b-2 border-emerald-500/30 hover:border-emerald-500 hover:bg-emerald-50/50 px-1 transition-all cursor-pointer"
        : "inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors";

    return (
        <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
            <div>
                <button
                    type="button"
                    className={buttonStyles}
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {label}
                    <ChevronDown className={`ml-1 h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} aria-hidden="true" />
                </button>
            </div>

            {isOpen && (
                <div
                    className="origin-top-right absolute left-0 mt-2 w-56 rounded-xl shadow-xl bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50 animate-fade-in-down overflow-hidden"
                    role="menu"
                >
                    <div className="py-1 max-h-60 overflow-y-auto custom-scrollbar" role="none">
                        {items.map((item, index) => (
                            <button
                                key={index}
                                className="text-slate-600 block w-full text-left px-4 py-3 text-sm hover:bg-emerald-50 hover:text-emerald-700 transition-colors border-b border-gray-50 last:border-0"
                                role="menuitem"
                                onClick={() => {
                                    if (item.action) item.action();
                                    if (onSelect) onSelect(item);
                                    setIsOpen(false);
                                }}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dropdown;
