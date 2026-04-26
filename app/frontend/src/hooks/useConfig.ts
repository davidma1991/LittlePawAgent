import { useState, useEffect, useCallback } from 'react'
import type { AgentConfig, McpConfig, ToolInfo } from '@/types'
import { fetchConfig, fetchTools, fetchModels, updateConfig } from '@/lib/api'

export function useConfig() {
  const [models, setModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('llama3.2')
  const [mode, setMode] = useState<'react' | 'plan_execute'>('react')
  const [tools, setTools] = useState<ToolInfo[]>([])
  const [agentConfig, setAgentConfig] = useState<AgentConfig | null>(null)
  const [mcpConfig, setMcpConfig] = useState<McpConfig | null>(null)
  const [mcpStatus, setMcpStatus] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(true)

  const loadAll = useCallback(async () => {
    setIsLoading(true)
    try {
      const [configData, toolsData, modelsData] = await Promise.all([
        fetchConfig(),
        fetchTools(),
        fetchModels(),
      ])
      setAgentConfig(configData.agent)
      setMcpConfig(configData.mcp)
      setMcpStatus(configData.mcp_status)
      setTools(toolsData)
      setModels(modelsData)
      if (modelsData.length > 0) {
        setSelectedModel(configData.agent?.ollama?.default_model || modelsData[0])
      }
    } catch (err) {
      console.error('Failed to load config:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const toggleTool = useCallback(async (toolName: string, enabled: boolean) => {
    if (!agentConfig) return
    const newConfig: AgentConfig = {
      ...agentConfig,
      tools: {
        ...agentConfig.tools,
        [toolName]: { ...agentConfig.tools[toolName], enabled },
      },
    }
    setAgentConfig(newConfig)
    await updateConfig({ agent: newConfig })
    const toolsData = await fetchTools()
    setTools(toolsData)
  }, [agentConfig])

  return {
    models,
    selectedModel,
    setSelectedModel,
    mode,
    setMode,
    tools,
    agentConfig,
    mcpConfig,
    mcpStatus,
    isLoading,
    refresh: loadAll,
    toggleTool,
  }
}
