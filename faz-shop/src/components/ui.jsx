// src/components/ui.jsx
export function Button({ children, variant = 'primary', size = 'md', loading, className = '', ...props }) {
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-5 py-2.5 text-sm', lg: 'px-7 py-3 text-base' };
  const base = 'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-gradient-to-r from-faz-green to-faz-orange hover:from-faz-orange hover:to-faz-red text-white shadow-md',
    outline: 'border-2 border-gray-300 text-gray-700 hover:border-faz-orange hover:text-faz-orange',
    danger: 'bg-faz-red text-white hover:bg-red-700',
    ghost: 'text-gray-600 hover:bg-gray-100',
  };
  return (
    <button
      disabled={loading || props.disabled}
      className={`${base} ${sizes[size]} ${variants[variant]} ${className}`}
      {...props}
    >
      {loading ? <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : null}
      {children}
    </button>
  );
}

export function Card({ children, className = '', padding = 'md' }) {
  const pad = { sm: 'p-3', md: 'p-5', lg: 'p-7' }[padding];
  return <div className={`bg-white border border-gray-200 rounded-2xl shadow-sm ${pad} ${className}`}>{children}</div>;
}

export function Input({ label, error, hint, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <input className="input-field" {...props} />
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
      {hint && !error && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

export function Textarea({ label, rows = 3, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <textarea rows={rows} className="input-field" {...props} />
    </div>
  );
}

export function Select({ label, children, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}
      <select className="input-field" {...props}>{children}</select>
    </div>
  );
}

export function Badge({ children, variant = 'default' }) {
  const v = {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    orange: 'bg-orange-100 text-orange-700',
    brand: 'bg-gradient-to-r from-faz-green to-faz-orange text-white',
  }[variant];
  return <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${v}`}>{children}</span>;
}

export function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4 border-2', md: 'w-8 h-8 border-2', lg: 'w-12 h-12 border-3', xl: 'w-16 h-16 border-4' };
  return (
    <div className={`${sizes[size]} border-faz-green border-t-faz-orange rounded-full animate-spin ${className}`} />
  );
}

export function EmptyState({ icon = '📭', title, description, action }) {
  return (
    <div className="text-center py-16">
      <div className="text-6xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      {description && <p className="text-sm text-gray-500 mt-1 max-w-md mx-auto">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}