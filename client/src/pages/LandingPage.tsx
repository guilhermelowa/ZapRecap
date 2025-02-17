import { FC } from 'react'
import FileUpload from '../components/FileUpload.tsx'
import Header from '../components/Header.tsx'

const LandingPage: FC = () => {
  return (
    <div className="landing-container">
      <Header />
      <FileUpload />
      <div className="landing-content">
        <section className="export-guide">
          <h2>How to Export Your WhatsApp Conversation</h2>
          <ul>
            <li>Open the WhatsApp conversation you want to export</li>
            <li>Tap the three-dot menu or settings icon</li>
            <li>Select "Export chat"</li>
            <li>Choose "Without Media" option</li>
            <li>Save the .zip file to your device</li>
            <li>You can upload the .zip file directly or the txt file inside</li>
          </ul>
        </section>

        <section className="privacy-notice">
          <h2>Privacy & Security</h2>
          <div className="privacy-content">
            <p>We take your privacy seriously. All uploaded messages are:</p>
            <ul>
              <li>Encrypted on our secure servers</li>
              <li>Automatically deleted within 24 hours</li>
              <li>Never shared or sold to third parties</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  )
}

export default LandingPage