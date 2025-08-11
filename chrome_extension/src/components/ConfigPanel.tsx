import React, { useState } from 'react'

interface Config {
  appToken: string
  personalBaseToken: string
}

interface Status {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

interface ConfigPanelProps {
  config: Config
  onSave: (config: Config) => void
  setStatus: (status: Status) => void
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ config, onSave, setStatus }) => {
  const [formData, setFormData] = useState(config)
  const [isTestingConnection, setIsTestingConnection] = useState(false)

  const handleInputChange = (field: keyof Config, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const testConnection = async () => {
    if (!formData.appToken || !formData.personalBaseToken) {
      setStatus({ type: 'error', message: '请填写完整的配置信息' })
      return
    }

    setIsTestingConnection(true)
    setStatus({ type: 'loading', message: '正在测试连接...' })

    try {
      // 发送消息到background script进行连接测试
      const response = await chrome.runtime.sendMessage({
        action: 'testConnection',
        config: formData
      })

      if (response.success) {
        setStatus({ type: 'success', message: '连接测试成功！' })
      } else {
        setStatus({ type: 'error', message: `连接测试失败: ${response.error}` })
      }
    } catch (error) {
      setStatus({ type: 'error', message: '连接测试失败，请检查网络连接' })
    } finally {
      setIsTestingConnection(false)
    }
  }

  const handleSave = () => {
    if (!formData.appToken || !formData.personalBaseToken) {
      setStatus({ type: 'error', message: '请填写完整的配置信息' })
      return
    }

    onSave(formData)
  }

  return (
    <div className="card">
      <h3>配置飞书认证信息</h3>
      
      <div className="form-group">
        <label htmlFor="appToken">APP_TOKEN (Base ID)</label>
        <input
          id="appToken"
          type="text"
          value={formData.appToken}
          onChange={(e) => handleInputChange('appToken', e.target.value)}
          placeholder="请输入APP_TOKEN"
        />
        <small style={{ color: '#666', fontSize: '12px' }}>
          从Base URL路径参数 /base/:app_token 获取
        </small>
      </div>

      <div className="form-group">
        <label htmlFor="personalBaseToken">PERSONAL_BASE_TOKEN</label>
        <input
          id="personalBaseToken"
          type="password"
          value={formData.personalBaseToken}
          onChange={(e) => handleInputChange('personalBaseToken', e.target.value)}
          placeholder="请输入PERSONAL_BASE_TOKEN"
        />
        <small style={{ color: '#666', fontSize: '12px' }}>
          从Base网页端获取的授权码
        </small>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          className="button"
          onClick={testConnection}
          disabled={isTestingConnection || !formData.appToken || !formData.personalBaseToken}
        >
          {isTestingConnection ? '测试中...' : '测试连接'}
        </button>
        
        <button
          className="button success"
          onClick={handleSave}
          disabled={!formData.appToken || !formData.personalBaseToken}
        >
          保存配置
        </button>
      </div>

      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f6ffed', borderRadius: '4px', fontSize: '12px' }}>
        <strong>使用说明：</strong>
        <ol style={{ margin: '8px 0', paddingLeft: '16px' }}>
          <li>打开飞书多维表格</li>
          <li>从URL中获取APP_TOKEN（/base/后面的字符串）</li>
          <li>在表格设置中生成PERSONAL_BASE_TOKEN</li>
          <li>填入上述信息并测试连接</li>
        </ol>
      </div>
    </div>
  )
}

export default ConfigPanel