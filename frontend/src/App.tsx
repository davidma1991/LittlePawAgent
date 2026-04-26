import { useChat } from '@/hooks/useChat'
import { useConfig } from '@/hooks/useConfig'
import { ChatWindow } from '@/components/Chat/ChatWindow'
import { Sidebar } from '@/components/Sidebar/Sidebar'

export default function App() {
  const {
    messages, isLoading,
    sendMessage, cancelStream, clearMessages,
  } = useChat()

  const {
    models, selectedModel, setSelectedModel,
    mode, setMode,
    tools, mcpConfig, mcpStatus,
    isLoading: configLoading,
    refresh, toggleTool,
  } = useConfig()

  const handleSend = (message: string) => {
    sendMessage(message, selectedModel, mode)
  }

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar
        models={models}
        selectedModel={selectedModel}
        onModelSelect={setSelectedModel}
        mode={mode}
        onModeChange={setMode}
        tools={tools}
        onToolToggle={toggleTool}
        mcpConfig={mcpConfig}
        mcpStatus={mcpStatus}
        onRefresh={refresh}
        onClear={clearMessages}
        isLoading={configLoading}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={handleSend}
          onCancel={cancelStream}
        />
      </main>
    </div>
  )
}
