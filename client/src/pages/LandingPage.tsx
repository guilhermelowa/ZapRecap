import { FC } from 'react'
import FileUpload from '../components/FileUpload.tsx'
import Header from '../components/Header.tsx'

const LandingPage: FC = () => {
  return (
    <div className="landing-container">
      <Header />
      <FileUpload />
    </div>
  )
}

export default LandingPage