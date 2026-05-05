import './ToolCard.css'

/**
 * 工具卡片元件。
 * 所有卡片統一透過 onClick 事件觸發，由 App.jsx 以 iframe 內嵌方式開啟。
 */
function ToolCard({ tool, onClick }) {
  return (
    <div className="tool-card" onClick={onClick}>
      <span className="tool-icon">{tool.icon}</span>
      <h3 className="tool-name">{tool.name}</h3>
      <p className="tool-description">{tool.description}</p>
    </div>
  )
}

export default ToolCard
