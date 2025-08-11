import React, { useState } from 'react'

interface Config {
  appToken: string
  personalBaseToken: string
}

interface Status {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
}

interface Field {
  name: string
  type: string
}

interface TableCreatorProps {
  config: Config
  onTableCreated: (tableId: string) => void
  setStatus: (status: Status) => void
}

const FIELD_TYPES = [
  { value: 'Text', label: '文本' },
  { value: 'Number', label: '数字' },
  { value: 'SingleSelect', label: '单选' },
  { value: 'MultiSelect', label: '多选' },
  { value: 'DateTime', label: '日期时间' },
  { value: 'Checkbox', label: '复选框' },
  { value: 'User', label: '人员' },
  { value: 'Phone', label: '电话号码' },
  { value: 'Url', label: '超链接' },
  { value: 'Attachment', label: '附件' },
  { value: 'Rating', label: '评分' },
  { value: 'Progress', label: '进度' }
]

const TableCreator: React.FC<TableCreatorProps> = ({ config, onTableCreated, setStatus }) => {
  const [tableName, setTableName] = useState('')
  const [fields, setFields] = useState<Field[]>([{ name: '标题', type: 'Text' }])
  const [isCreating, setIsCreating] = useState(false)

  const addField = () => {
    setFields(prev => [...prev, { name: '', type: 'Text' }])
  }

  const removeField = (index: number) => {
    if (fields.length > 1) {
      setFields(prev => prev.filter((_, i) => i !== index))
    }
  }

  const updateField = (index: number, field: Partial<Field>) => {
    setFields(prev => prev.map((f, i) => i === index ? { ...f, ...field } : f))
  }

  const createTable = async () => {
    if (!tableName.trim()) {
      setStatus({ type: 'error', message: '请输入表格名称' })
      return
    }

    if (fields.some(f => !f.name.trim())) {
      setStatus({ type: 'error', message: '请填写所有字段名称' })
      return
    }

    setIsCreating(true)
    setStatus({ type: 'loading', message: '正在创建表格...' })

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'createTable',
        config,
        tableName: tableName.trim(),
        fields: fields.filter(f => f.name.trim())
      })

      if (response.success) {
        setStatus({ type: 'success', message: `表格创建成功！表格ID: ${response.tableId}` })
        onTableCreated(response.tableId)
      } else {
        setStatus({ type: 'error', message: `创建失败: ${response.error}` })
      }
    } catch (error) {
      setStatus({ type: 'error', message: '创建表格失败，请检查网络连接' })
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="card">
      <h3>创建新表格</h3>
      
      <div className="form-group">
        <label htmlFor="tableName">表格名称</label>
        <input
          id="tableName"
          type="text"
          value={tableName}
          onChange={(e) => setTableName(e.target.value)}
          placeholder="请输入表格名称"
        />
      </div>

      <div className="form-group">
        <label>字段配置</label>
        <div className="field-list">
          {fields.map((field, index) => (
            <div key={index} className="field-item">
              <input
                type="text"
                value={field.name}
                onChange={(e) => updateField(index, { name: e.target.value })}
                placeholder="字段名称"
              />
              <select
                value={field.type}
                onChange={(e) => updateField(index, { type: e.target.value })}
              >
                {FIELD_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField(index)}
                >
                  删除
                </button>
              )}
            </div>
          ))}
        </div>
        <button
          type="button"
          className="button add-field"
          onClick={addField}
        >
          + 添加字段
        </button>
      </div>

      <button
        className="button success"
        onClick={createTable}
        disabled={isCreating || !tableName.trim()}
        style={{ width: '100%', marginTop: '16px' }}
      >
        {isCreating ? '创建中...' : '创建表格'}
      </button>

      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff7e6', borderRadius: '4px', fontSize: '12px' }}>
        <strong>提示：</strong>
        <ul style={{ margin: '8px 0', paddingLeft: '16px' }}>
          <li>表格将在当前Base中创建</li>
          <li>默认包含一个"标题"字段</li>
          <li>可以添加多个不同类型的字段</li>
          <li>创建成功后可以直接写入数据</li>
        </ul>
      </div>
    </div>
  )
}

export default TableCreator