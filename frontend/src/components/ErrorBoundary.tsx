import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={styles.container}>
          <div style={styles.card}>
            <h2 style={styles.heading}>Something went wrong</h2>
            <p style={styles.message}>
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <button
              style={styles.button}
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#1a1a1e',
    color: '#e2e8f0',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif',
  },
  card: {
    textAlign: 'center' as const,
    padding: 32,
    maxWidth: 420,
  },
  heading: {
    fontSize: 20,
    fontWeight: 600,
    marginBottom: 12,
  },
  message: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 24,
    lineHeight: 1.5,
  },
  button: {
    padding: '10px 24px',
    borderRadius: 8,
    border: 'none',
    backgroundColor: '#2563eb',
    color: 'white',
    fontSize: 14,
    fontWeight: 500,
    cursor: 'pointer',
  },
};
