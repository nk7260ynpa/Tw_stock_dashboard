import ToolCard from './ToolCard'
import './LaunchPad.css'

function LaunchPad({ tools, onSelect }) {
  return (
    <div className="launchpad-grid">
      {tools.map((tool) => (
        <ToolCard key={tool.id} tool={tool} onClick={() => onSelect(tool)} />
      ))}
    </div>
  )
}

export default LaunchPad
