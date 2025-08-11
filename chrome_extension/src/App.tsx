import { useState, useEffect } from 'react'
import ConfigPanel from './components/ConfigPanel'
import TableCreator from './components/TableCreator'
import DataWriter from './components/DataWriter'
import StatusDisplay from './components/StatusDisplay'
import './App.css'

interface Config {
  appToken: string
  personalBaseToken: string
}

interface Status {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

function App() {
  const [config, setConfig] = useState<Config>({ appToken: '', personalBaseToken: '' })
  const [status, setStatus] = useState<Status>({ type: 'idle', message: '' })
  const [currentTableId, setCurrentTableId] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'config' | 'create' | 'write'>('config')

  // 加载保存的配置
  useEffect(() => {
    chrome.storage.local.get(['appToken', 'personalBaseToken'], (result) => {
      if (result.appToken && result.personalBaseToken) {
        setConfig({
          appToken: result.appToken,
          personalBaseToken: result.personalBaseToken
        })
        setActiveTab('create')
      }
    })
  }, [])

  const handleConfigSave = (newConfig: Config) => {
    setConfig(newConfig)
    chrome.storage.local.set(newConfig)
    setStatus({ type: 'success', message: '配置保存成功' })
    setActiveTab('create')
  }

  const handleTableCreated = (tableId: string) => {
    setCurrentTableId(tableId)
    setActiveTab('write')
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'config':
        return (
          <ConfigPanel
            config={config}
            onSave={handleConfigSave}
            setStatus={setStatus}
          />
        )
      case 'create':
        return (
          <TableCreator
            config={config}
            onTableCreated={handleTableCreated}
            setStatus={setStatus}
          />
        )
      case 'write':
        return (
          <DataWriter
            config={config}
            tableId={currentTableId}
            setStatus={setStatus}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="app">
      <div className="header">
        <h1>飞书多维表格助手</h1>
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'config' ? 'active' : ''}`}
            onClick={() => setActiveTab('config')}
          >
            配置
          </button>
          <button
            className={`tab ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
            disabled={!config.appToken || !config.personalBaseToken}
          >
            创建表格
          </button>
          <button
            className={`tab ${activeTab === 'write' ? 'active' : ''}`}
            onClick={() => setActiveTab('write')}
            disabled={!currentTableId}
          >
            写入数据
          </button>
        </div>
      </div>
      
      <div className="content">
        {renderContent()}
      </div>
      
      <StatusDisplay status={status} />
    </div>
  )
}

export default App