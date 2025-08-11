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
  ui_type?: string
}

interface SearchReplaceProps {
  config: Config
  tableId: string
  setStatus: (status: Status) => void
}

const SearchReplace: React.FC<SearchReplaceProps> = ({ config, tableId, setStatus }) => {
  const [sourceText, setSourceText] = useState('')
  const [targetText, setTargetText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [textFields, setTextFields] = useState<Field[]>([])
  const [isLoadingFields, setIsLoadingFields] = useState(false)
  const [previewMode, setPreviewMode] = useState(false)
  const [previewResults, setPreviewResults] = useState<any[]>([])

  // 获取文本字段信息
  useEffect(() => {
    const fetchTextFields = async () => {
      setIsLoadingFields(true)
      setStatus({ type: 'loading', message: '正在获取表格字段信息...' })

      try {
        const response = await chrome.runtime.sendMessage({
          action: 'getTableFields',
          config,
          tableId
        })

        if (response.success) {
          // 筛选出文本类型字段
          const textFieldsOnly = response.fields.filter((field: Field) => 
            field.type === '1' || field.ui_type === 'Text'
          )
          setTextFields(textFieldsOnly)
          
          if (textFieldsOnly.length === 0) {
            setStatus({ type: 'error', message: '表格中没有文本字段可以进行查找替换' })
          } else {
            setStatus({ type: 'success', message: `找到 ${textFieldsOnly.length} 个文本字段` })
          }
        } else {
          setStatus({ type: 'error', message: `获取字段失败: ${response.error}` })
        }
      } catch (error) {
        setStatus({ type: 'error', message: '获取字段信息失败，请检查网络连接' })
      } finally {
        setIsLoadingFields(false)
      }
    }

    if (tableId) {
      fetchTextFields()
    }
  }, [tableId, config, setStatus])

  // 预览查找结果
  const previewSearch = async () => {
    if (!sourceText.trim()) {
      setStatus({ type: 'error', message: '请输入要查找的文本' })
      return
    }

    setIsProcessing(true)
    setStatus({ type: 'loading', message: '正在预览查找结果...' })

    try {
      // 获取所有记录
      const response = await chrome.runtime.sendMessage({
        action: 'getRecords',
        config,
        tableId,
        pageSize: 100
      })

      if (response.success) {
        const textFieldNames = textFields.map(field => field.field_name)
        const matchingRecords = []

        for (const record of response.records) {
          const fields = record.fields
          const matchingFields = []
          
          for (const [key, value] of Object.entries(fields)) {
            if (textFieldNames.includes(key) && typeof value === 'string' && value.includes(sourceText)) {
              matchingFields.push({
                fieldName: key,
                originalValue: value,
                newValue: value.replace(new RegExp(sourceText, 'g'), targetText || '[替换文本]')
              })
            }
          }
          
          if (matchingFields.length > 0) {
            matchingRecords.push({
              recordId: record.record_id,
              fields: matchingFields
            })
          }
        }

        setPreviewResults(matchingRecords)
        setPreviewMode(true)
        setStatus({ 
          type: 'success', 
          message: `找到 ${matchingRecords.length} 条记录包含要查找的文本` 
        })
      } else {
        setStatus({ type: 'error', message: `获取记录失败: ${response.error}` })
      }
    } catch (error) {
      setStatus({ type: 'error', message: '预览失败，请检查网络连接' })
    } finally {
      setIsProcessing(false)
    }
  }

  // 执行批量替换
  const executeReplace = async () => {
    if (!sourceText.trim()) {
      setStatus({ type: 'error', message: '请输入要查找的文本' })
      return
    }

    if (!targetText.trim()) {
      setStatus({ type: 'error', message: '请输入替换后的文本' })
      return
    }

    setIsProcessing(true)
    setStatus({ type: 'loading', message: '正在执行批量替换...' })

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'searchAndReplace',
        config,
        tableId,
        sourceText,
        targetText
      })

      if (response.success) {
        setStatus({ 
          type: 'success', 
          message: response.message || `替换完成，共更新 ${response.updatedCount} 条记录` 
        })
        // 清空输入
        setSourceText('')
        setTargetText('')
        setPreviewMode(false)
        setPreviewResults([])
      } else {
        setStatus({ type: 'error', message: `替换失败: ${response.error}` })
      }
    } catch (error) {
      setStatus({ type: 'error', message: '替换失败，请检查网络连接' })
    } finally {
      setIsProcessing(false)
    }
  }

  if (isLoadingFields) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '20px' }}>
          正在加载表格信息...
        </div>
      </div>
    )
  }

  if (textFields.length === 0) {
    return (
      <div className="card">
        <h3>批量查找替换</h3>
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          当前表格没有文本字段，无法进行查找替换操作
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>批量查找替换</h3>
      
      <div style={{ marginBottom: '12px', fontSize: '12px', color: '#666' }}>
        表格ID: {tableId} | 文本字段: {textFields.map(f => f.field_name).join(', ')}
      </div>

      <div className="form-group">
        <label>查找文本</label>
        <input
          type="text"
          value={sourceText}
          onChange={(e) => setSourceText(e.target.value)}
          placeholder="请输入要查找的文本"
          disabled={isProcessing}
        />
      </div>

      <div className="form-group">
        <label>替换为</label>
        <input
          type="text"
          value={targetText}
          onChange={(e) => setTargetText(e.target.value)}
          placeholder="请输入替换后的文本"
          disabled={isProcessing}
        />
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button
          className="button"
          onClick={previewSearch}
          disabled={isProcessing || !sourceText.trim()}
          style={{ flex: 1 }}
        >
          {isProcessing ? '预览中...' : '预览查找'}
        </button>
        
        <button
          className="button warning"
          onClick={executeReplace}
          disabled={isProcessing || !sourceText.trim() || !targetText.trim()}
          style={{ flex: 1 }}
        >
          {isProcessing ? '替换中...' : '执行替换'}
        </button>
      </div>

      {previewMode && previewResults.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ marginBottom: '8px', fontSize: '14px' }}>预览结果 ({previewResults.length} 条记录)</h4>
          <div style={{ 
            maxHeight: '200px', 
            overflowY: 'auto', 
            border: '1px solid #ddd', 
            borderRadius: '4px',
            padding: '8px',
            backgroundColor: '#f9f9f9'
          }}>
            {previewResults.slice(0, 5).map((record, index) => (
              <div key={record.recordId} style={{ marginBottom: '12px', fontSize: '12px' }}>
                <div style={{ fontWeight: 'bold', color: '#333' }}>记录 {index + 1}:</div>
                {record.fields.map((field: any, fieldIndex: number) => (
                  <div key={fieldIndex} style={{ marginLeft: '8px', marginTop: '4px' }}>
                    <div style={{ color: '#666' }}>{field.fieldName}:</div>
                    <div style={{ color: '#d32f2f' }}>- {field.originalValue}</div>
                    <div style={{ color: '#2e7d32' }}>+ {field.newValue}</div>
                  </div>
                ))}
              </div>
            ))}
            {previewResults.length > 5 && (
              <div style={{ textAlign: 'center', color: '#666', fontSize: '12px' }}>
                还有 {previewResults.length - 5} 条记录...
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff3cd', borderRadius: '4px', fontSize: '12px' }}>
        <strong>⚠️ 注意事项：</strong>
        <ul style={{ margin: '8px 0', paddingLeft: '16px' }}>
          <li>批量替换操作不可撤销，请谨慎操作</li>
          <li>建议先使用"预览查找"确认要替换的内容</li>
          <li>只会替换文本类型字段中的内容</li>
          <li>替换操作会匹配所有包含查找文本的位置</li>
        </ul>
      </div>
    </div>
  )
}

export default SearchReplace