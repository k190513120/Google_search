import React from 'react'

interface Status {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

interface StatusDisplayProps {
  status: Status
}

const StatusDisplay: React.FC<StatusDisplayProps> = ({ status }) => {
  if (status.type === 'idle' || !status.message) {
    return null
  }

  const getStatusIcon = () => {
    switch (status.type) {
      case 'loading':
        return '⏳'
      case 'success':
        return '✅'
      case 'error':
        return '❌'
      default:
        return ''
    }
  }

  return (
    <div className={`status ${status.type}`}>
      <span style={{ marginRight: '8px' }}>{getStatusIcon()}</span>
      {status.message}
    </div>
  )
}

export default StatusDisplay