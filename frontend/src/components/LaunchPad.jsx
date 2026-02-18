import ToolCard from './ToolCard'
import './LaunchPad.css'

function LaunchPad({ tools }) {
  return (
    <div className="launchpad-grid">
      {tools.map((tool) => (
        <ToolCard key={tool.id} tool={tool} />
      ))}
    </div>
  )
}

export default LaunchPad
