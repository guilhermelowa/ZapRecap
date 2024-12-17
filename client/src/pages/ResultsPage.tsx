import { FC } from 'react'
import { useLocation } from 'react-router-dom'

const ResultsPage: FC = () => {
  const location = useLocation()
  const analysis = location.state?.analysis

  return (
    <div className="results-container">
      <h1>Analysis Results</h1>
      {/* Results will go here */}
    </div>
  )
}

export default ResultsPage