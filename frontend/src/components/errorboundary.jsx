import { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
          <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 space-y-6 border border-gray-100">
            <h2 className="text-2xl font-semibold text-red-600">Something went wrong</h2>
            <p className="text-gray-600">
              An error occurred. Please refresh the page and try again.
            </p>
            <button
              onClick={() => {
                window.location.reload();
              }}
              className="w-full px-4 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors"
            >
              Refresh Page
            </button>
            {this.state.error && (
              <details className="text-xs text-gray-500">
                <summary>Error details</summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

