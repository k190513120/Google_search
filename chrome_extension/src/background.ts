// Background script for Chrome extension

interface Config {
  appToken: string
  personalBaseToken: string
}

interface Field {
  name: string
  type: string
}

// Base SDK API基础URL - 使用Base SDK专用端点
const BASE_API_BASE = 'https://base-api.feishu.cn/open-apis'

// 创建HTTP请求的通用函数 - 使用Base SDK鉴权
async function makeFeishuRequest(endpoint: string, config: Config, options: RequestInit = {}) {
  const url = `${BASE_API_BASE}${endpoint}`
  
  // Base SDK认证方式：使用personalBaseToken作为Bearer token，appToken作为X-Base-Token
  const headers = {
    'Authorization': `Bearer ${config.personalBaseToken}`,
    'X-Base-Token': config.appToken,
    'Content-Type': 'application/json',
    ...options.headers
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP ${response.status}: ${errorText}`)
  }

  return response.json()
}

// 测试连接
async function testConnection(config: Config) {
  try {
    // 尝试获取Base信息来测试连接
    const response = await makeFeishuRequest(`/bitable/v1/apps/${config.appToken}`, config)
    return { success: true, data: response }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 创建表格
async function createTable(config: Config, tableName: string, fields: Field[]) {
  try {
    // 构建字段配置
    const fieldConfigs = fields.map(field => ({
      field_name: field.name,
      type: getFeishuFieldType(field.type)
    }))

    const requestBody = {
      table: {
        name: tableName,
        default_view_name: '表格视图',
        fields: fieldConfigs
      }
    }

    const response = await makeFeishuRequest(
      `/bitable/v1/apps/${config.appToken}/tables`,
      config,
      {
        method: 'POST',
        body: JSON.stringify(requestBody)
      }
    )

    if (response.code === 0) {
      return { success: true, tableId: response.data.table_id }
    } else {
      return { success: false, error: response.msg || '创建表格失败' }
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 获取表格字段信息
async function getTableFields(config: Config, tableId: string) {
  try {
    const response = await makeFeishuRequest(
      `/bitable/v1/apps/${config.appToken}/tables/${tableId}/fields`,
      config
    )

    if (response.code === 0) {
      return { success: true, fields: response.data.items }
    } else {
      return { success: false, error: response.msg || '获取字段信息失败' }
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 写入记录
async function writeRecord(config: Config, tableId: string, recordData: Record<string, any>) {
  try {
    const requestBody = {
      fields: recordData
    }

    const response = await makeFeishuRequest(
      `/bitable/v1/apps/${config.appToken}/tables/${tableId}/records`,
      config,
      {
        method: 'POST',
        body: JSON.stringify(requestBody)
      }
    )

    if (response.code === 0) {
      return { success: true, recordId: response.data.record.record_id }
    } else {
      return { success: false, error: response.msg || '写入记录失败' }
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 获取记录列表
async function getRecords(config: Config, tableId: string, pageSize: number = 100) {
  try {
    const response = await makeFeishuRequest(
      `/bitable/v1/apps/${config.appToken}/tables/${tableId}/records?page_size=${pageSize}`,
      config
    )

    if (response.code === 0) {
      return { success: true, records: response.data.items }
    } else {
      return { success: false, error: response.msg || '获取记录失败' }
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 批量更新记录
async function batchUpdateRecords(config: Config, tableId: string, records: Array<{record_id: string, fields: Record<string, any>}>) {
  try {
    const requestBody = {
      records: records
    }

    const response = await makeFeishuRequest(
      `/bitable/v1/apps/${config.appToken}/tables/${tableId}/records/batch_update`,
      config,
      {
        method: 'POST',
        body: JSON.stringify(requestBody)
      }
    )

    if (response.code === 0) {
      return { success: true, updatedRecords: response.data.records }
    } else {
      return { success: false, error: response.msg || '批量更新记录失败' }
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 批量查找替换文本
async function searchAndReplace(config: Config, tableId: string, sourceText: string, targetText: string) {
  try {
    // 1. 获取表格字段信息
    const fieldsResult = await getTableFields(config, tableId)
    if (!fieldsResult.success) {
      return { success: false, error: '获取字段信息失败: ' + fieldsResult.error }
    }

    // 2. 筛选出文本类型字段
    const textFields = fieldsResult.fields.filter((field: any) => 
      field.type === '1' || field.ui_type === 'Text'
    )
    const textFieldNames = textFields.map((field: any) => field.field_name)

    if (textFieldNames.length === 0) {
      return { success: false, error: '表格中没有文本字段' }
    }

    // 3. 获取所有记录
    const recordsResult = await getRecords(config, tableId)
    if (!recordsResult.success) {
      return { success: false, error: '获取记录失败: ' + recordsResult.error }
    }

    // 4. 查找需要替换的记录
    const recordsNeedUpdate: Array<{record_id: string, fields: Record<string, any>}> = []
    
    for (const record of recordsResult.records) {
      const recordId = record.record_id
      const fields = record.fields
      const newFields: Record<string, any> = {}
      
      for (const [key, value] of Object.entries(fields)) {
        if (textFieldNames.includes(key) && typeof value === 'string') {
          const newValue = value.replace(new RegExp(sourceText, 'g'), targetText)
          if (newValue !== value) {
            newFields[key] = newValue
          }
        }
      }
      
      if (Object.keys(newFields).length > 0) {
        recordsNeedUpdate.push({
          record_id: recordId,
          fields: newFields
        })
      }
    }

    if (recordsNeedUpdate.length === 0) {
      return { success: true, message: '没有找到需要替换的内容', updatedCount: 0 }
    }

    // 5. 批量更新记录
    const updateResult = await batchUpdateRecords(config, tableId, recordsNeedUpdate)
    if (!updateResult.success) {
      return { success: false, error: '批量更新失败: ' + updateResult.error }
    }

    return { 
      success: true, 
      message: `成功替换 ${recordsNeedUpdate.length} 条记录`,
      updatedCount: recordsNeedUpdate.length,
      textFields: textFieldNames
    }
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : '未知错误' }
  }
}

// 将UI字段类型转换为飞书API字段类型
function getFeishuFieldType(uiType: string): number {
  const typeMap: Record<string, number> = {
    'Text': 1,        // 多行文本
    'Number': 2,      // 数字
    'SingleSelect': 3, // 单选
    'MultiSelect': 4,  // 多选
    'DateTime': 5,     // 日期
    'Checkbox': 7,     // 复选框
    'User': 11,        // 人员
    'Phone': 13,       // 电话号码
    'Url': 15,         // 超链接
    'Attachment': 17,  // 附件
    'Rating': 19,      // 评分
    'Progress': 20     // 进度
  }
  
  return typeMap[uiType] || 1 // 默认为文本类型
}

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  const handleAsync = async () => {
    try {
      switch (request.action) {
        case 'testConnection':
          return await testConnection(request.config)
        
        case 'createTable':
          return await createTable(request.config, request.tableName, request.fields)
        
        case 'getTableFields':
          return await getTableFields(request.config, request.tableId)
        
        case 'writeRecord':
          return await writeRecord(request.config, request.tableId, request.recordData)
        
        case 'getRecords':
          return await getRecords(request.config, request.tableId, request.pageSize)
        
        case 'batchUpdateRecords':
          return await batchUpdateRecords(request.config, request.tableId, request.records)
        
        case 'searchAndReplace':
          return await searchAndReplace(request.config, request.tableId, request.sourceText, request.targetText)
        
        default:
          return { success: false, error: '未知操作' }
      }
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : '未知错误' }
    }
  }

  handleAsync().then(sendResponse)
  return true // 保持消息通道开放
})

// 扩展安装时的初始化
chrome.runtime.onInstalled.addListener(() => {
  console.log('飞书多维表格助手已安装')
})