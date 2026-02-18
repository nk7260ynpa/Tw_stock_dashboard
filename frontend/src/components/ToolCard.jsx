import './ToolCard.css'

function ToolCard({ tool }) {
  return (
    <div className="tool-card">
      <span className="tool-icon">{tool.icon}</span>
      <h3 className="tool-name">{tool.name}</h3>
      <p className="tool-description">{tool.description}</p>
    </div>
  )
}

export default ToolCard
