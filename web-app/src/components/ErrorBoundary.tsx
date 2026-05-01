import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: '' }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo: errorInfo.componentStack || '' })
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: 20,
          color: '#fff',
          background: '#1a1a2e',
          minHeight: '100vh',
          fontFamily: 'monospace',
        }}>
          <h2 style={{ color: '#ff6b6b' }}>⚠️ 组件渲染错误</h2>
          <details style={{ marginTop: 10 }}>
            <summary style={{ cursor: 'pointer', marginBottom: 10 }}>
              错误信息（点击展开）
            </summary>
            <pre style={{
              background: '#000',
              padding: 10,
              borderRadius: 4,
              fontSize: 12,
              overflow: 'auto',
              maxHeight: 400,
            }}>
              {this.state.error?.toString()}
              {'\n\nComponent Stack:\n'}
              {this.state.errorInfo}
            </pre>
          </details>
          <button
            onClick={() => this.setState({ hasError: false, error: null, errorInfo: '' })}
            style={{
              marginTop: 15,
              padding: '8px 16px',
              background: '#4A90D9',
              color: '#fff',
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer',
            }}
          >
            重试
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
