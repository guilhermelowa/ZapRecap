import { FC, ChangeEvent, DragEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const FileUpload: FC = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')
  const navigate = useNavigate()

  const validateFile = (file: File): boolean => {
    if (!file.name.endsWith('.txt')) {
      setError('Please upload a .txt file')
      return false
    }
    return true
  }

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      setFile(file)
      setError('')
      // TODO: Call API and navigate to results
    }
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) handleFile(droppedFile)
  }

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) handleFile(selectedFile)
  }

  return (
    <div 
      className={`upload-zone ${isDragging ? 'dragging' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".txt"
        onChange={handleFileInput}
        id="file-input"
        className="hidden-input"
      />
      <label htmlFor="file-input" className="upload-label">
        <div className="upload-content">
          <svg className="upload-icon" viewBox="0 0 24 24" width="48" height="48">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          <p>Drop your WhatsApp chat file here or click to browse</p>
          {file && <p className="file-name">Selected: {file.name}</p>}
          {error && <p className="error-message">{error}</p>}
        </div>
      </label>
    </div>
  )
}

export default FileUpload