import { FC, ChangeEvent, DragEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../services/axiosConfig'
import axios from 'axios'

const FileUpload: FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')
  const navigate = useNavigate()

  const validateFile = (file: File | undefined): file is File => {
    if (!file) {
      setError('Please upload a valid file')
      return false
    }
    if (!file.name.endsWith('.txt') && !file.name.endsWith('.zip')) {
      setError('Please upload a .txt or .zip file')
      return false
    }
    return true
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (validateFile(droppedFile)) {
      setSelectedFile(droppedFile);
      setError('');
    }
  }

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (validateFile(file)) {
      setSelectedFile(file);
      setError('');
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please upload a valid file');
      return;
    }
    setIsLoading(true);
    const reader = new FileReader();

    reader.onload = async (_e) => {
      
      try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await apiClient.post('/analyze', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        navigate('/results', { 
          state: {
             result: response.data
          } 
        })
      } catch (error) {
        console.error('Error details:', error);
        if (axios.isAxiosError(error)) {
          console.error('Response:', error.response);
          console.error('Request:', error.request);
        }
        setError('Failed to analyze file. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    // Only read text files as text, for zip files we'll send the file directly
    if (selectedFile.name.endsWith('.txt')) {
      reader.readAsText(selectedFile);
    } else {
      handleSubmit(); // Directly submit for zip files
    }
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
        accept=".txt,.zip"
        onChange={handleFileInput}
        id="file-input"
        className="hidden-input"
      />
      <label htmlFor="file-input" className="upload-label">
        <div className="upload-content">
          <svg className="upload-icon" viewBox="0 0 24 24" width="48" height="48">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          <p>Drop your WhatsApp chat .txt or .zip file here or click to browse</p>
          {selectedFile && <p className="file-name">Selected: {selectedFile.name}</p>}
          {error && <p className="error-message">{error}</p>}
        </div>
      </label>
      <button 
        onClick={handleSubmit}
        disabled={!selectedFile || isLoading}
      >
        {isLoading ? 'Processing...' : 'Analyze File'}
      </button>
      {isLoading && <div>Loading...</div>}
    </div>
  )
}

export default FileUpload