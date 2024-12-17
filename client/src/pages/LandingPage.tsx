import { FC } from 'react'
import FileUpload from '../components/FileUpload.tsx'

const LandingPage: FC = () => {
  return (
    <div className="landing-container">
      <header className="whatsapp-header">
        <h1>WhatsApp Chat Analyzer</h1>
      </header>
      <FileUpload />
    </div>
  )
}

export default LandingPage