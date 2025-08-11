import React, { useState, useEffect } from 'react'

interface Config {
  appToken: string
  personalBaseToken: string
}

interface Status {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

interface Field {
  field_id: string
  field_name: string
  type: string
}

interface DataWriterProps {
  config: Config
  tableId: string
  setStatus: (status: Status) => void
}

const DataWriter: React.FC<DataWriterProps> = ({ config, tableId, setStatus }) => {
  const [fields, setFields] = useState<Field[]>([])
  const [recordData, setRecordData] = useState<Record<string, any>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isWriting, setIsWriting] = useState(false)
  const [jsonMode, setJsonMode] = useState(false)
  const [jsonData, setJsonData] = useState('')

  // 获取表格字段信息
  useEffect(() => {
    const fetchFields = async () => {
      setIsLoading(true)
      setStatus({ type: 'loading', message: '正在获取表格字段信息...' })

      try {
        const response = await chrome.runtime.sendMessage({
          action: 'getTableFields',
          config,
          tableId
        })

        if (response.success) {
          setFields(response.fields)
          // 初始化记录数据
          const initialData: Record<string, any> = {}
          response.fields.forEach((field: Field) => {
            initialData[field.field_name] = ''
          })
          setRecordData(initialData)
          setStatus({ type: 'success', message: '字段信息获取成功' })
        } else {
          setStatus({ type: 'error', message: `获取字段失败: ${response.error}` })
        }
      } catch (error) {
        setStatus({ type: 'error', message: '获取字段信息失败，请检查网络连接' })
      } finally {
        setIsLoading(false)
      }
    }

    if (tableId) {
      fetchFields()
    }
  }, [tableId, config, setStatus])

  const handleFieldChange = (fieldName: string, value: any) => {
    setRecordData(prev => ({ ...prev, [fieldName]: value }))
  }

  const handleJsonChange = (value: string) => {
    setJsonData(value)
    try {
      const parsed = JSON.parse(value)
      setRecordData(parsed)
    } catch (error) {
      // JSON格式错误，不更新recordData
    }
  }

  const toggleJsonMode = () => {
    if (!jsonMode) {
      // 切换到JSON模式，将当前数据转换为JSON
      setJsonData(JSON.stringify(recordData, null, 2))
    } else {
      // 切换到表单模式，尝试解析JSON
      try {
        const parsed = JSON.parse(jsonData)
        setRecordData(parsed)
      } catch (error) {
        setStatus({ type: 'error', message: 'JSON格式错误，请检查格式' })
        return
      }
    }
    setJsonMode(!jsonMode)
  }

  const writeData = async () => {
    const dataToWrite = jsonMode ? (() => {
      try {
        return JSON.parse(jsonData)
      } catch (error) {
        setStatus({ type: 'error', message: 'JSON格式错误，请检查格式' })
        return null
      }
    })() : recordData

    if (!dataToWrite) return

    // 检查是否有数据
    const hasData = Object.values(dataToWrite).some(value => 
      value !== null && value !== undefined && value !== ''
    )

    if (!hasData) {
      setStatus({ type: 'error', message: '请至少填写一个字段的数据' })
      return
    }

    setIsWriting(true)
    setStatus({ type: 'loading', message: '正在写入数据...' })

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'writeRecord',
        config,
        tableId,
        recordData: dataToWrite
      })

      if (response.success) {
        setStatus({ type: 'success', message: `数据写入成功！记录ID: ${response.recordId}` })
        // 清空表单
        if (!jsonMode) {
          const emptyData: Record<string, any> = {}
          fields.forEach(field => {
            emptyData[field.field_name] = ''
          })
          setRecordData(emptyData)
        } else {
          setJsonData('')
        }
      } else {
        setStatus({ type: 'error', message: `写入失败: ${response.error}` })
      }
    } catch (error) {
      setStatus({ type: 'error', message: '写入数据失败，请检查网络连接' })
    } finally {
      setIsWriting(false)
    }
  }

  const renderFieldInput = (field: Field) => {
    const value = recordData[field.field_name] || ''
    
    switch (field.type) {
      case 'Number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleFieldChange(field.field_name, e.target.value ? Number(e.target.value) : '')}
            placeholder={`请输入${field.field_name}`}
          />
        )
      case 'Checkbox':
        return (
          <input
            type="checkbox"
            checked={!!value}
            onChange={(e) => handleFieldChange(field.field_name, e.target.checked)}
          />
        )
      case 'DateTime':
        return (
          <input
            type="datetime-local"
            value={value}
            onChange={(e) => handleFieldChange(field.field_name, e.target.value)}
          />
        )
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleFieldChange(field.field_name, e.target.value)}
            placeholder={`请输入${field.field_name}`}
          />
        )
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          正在加载表格信息...
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3>写入数据</h3>
        <button
          className="button"
          onClick={toggleJsonMode}
          style={{ fontSize: '12px', padding: '4px 8px' }}
        >
          {jsonMode ? '表单模式' : 'JSON模式'}
        </button>
      </div>
      
      <div style={{ marginBottom: '12px', fontSize: '12px', color: '#666' }}>
        表格ID: {tableId}
      </div>

      {jsonMode ? (
        <div className="form-group">
          <label>JSON数据</label>
          <textarea
            className="json-editor"
            value={jsonData}
            onChange={(e) => handleJsonChange(e.target.value)}
            placeholder='请输入JSON格式的数据，例如：\n{\n  "标题": "示例标题",\n  "内容": "示例内容"\n}'
            rows={10}
          />
        </div>
      ) : (
        <div>
          {fields.map(field => (
            <div key={field.field_id} className="form-group">
              <label>{field.field_name} ({field.type})</label>
              {renderFieldInput(field)}
            </div>
          ))}
        </div>
      )}

      <button
        className="button warning"
        onClick={writeData}
        disabled={isWriting}
        style={{ width: '100%', marginTop: '16px' }}
      >
        {isWriting ? '写入中...' : '写入数据'}
      </button>

      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f6ffed', borderRadius: '4px', fontSize: '12px' }}>
        <strong>使用说明：</strong>
        <ul style={{ margin: '8px 0', paddingLeft: '16px' }}>
          <li>表单模式：逐个填写字段值</li>
          <li>JSON模式：直接编辑JSON格式数据</li>
          <li>支持多种字段类型的数据输入</li>
          <li>写入成功后表单会自动清空</li>
        </ul>
      </div>
    </div>
  )
}

export default DataWriter