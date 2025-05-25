'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, CheckCircle, AlertCircle, X, MessageSquare, Smartphone } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'

interface ImportResult {
  success: boolean
  message: string
  details?: {
    imported: number
    total: number
    errors?: string[]
  }
}

export function WhatsAppImport({ onClose }: { onClose: () => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [chatName, setChatName] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [showInstructions, setShowInstructions] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      if (file.name.endsWith('.txt')) {
        setFile(file)
        // Try to extract chat name from filename
        const name = file.name.replace('.txt', '').replace('WhatsApp Chat with ', '')
        setChatName(name)
      }
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt']
    },
    maxFiles: 1
  })

  const handleUpload = async () => {
    if (!file || !chatName) return

    setIsUploading(true)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('chat_name', chatName)

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/whatsapp/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      setResult(response.data)
    } catch (error: unknown) {
      const errorMessage = axios.isAxiosError(error) 
        ? error.response?.data?.detail || 'Failed to import chat'
        : 'Failed to import chat'
      
      setResult({
        success: false,
        message: errorMessage
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-2xl p-6 max-w-lg w-full border border-white/10"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-green-400" />
            </div>
            <h2 className="text-xl font-semibold text-white">Import WhatsApp Chat</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {!result ? (
          <>
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
                ${isDragActive 
                  ? 'border-green-400 bg-green-500/10' 
                  : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
                }
              `}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              {file ? (
                <div className="space-y-2">
                  <FileText className="w-8 h-8 text-green-400 mx-auto" />
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-sm text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <>
                  <p className="text-white mb-2">
                    {isDragActive ? 'Drop the file here' : 'Drag & drop your WhatsApp export'}
                  </p>
                  <p className="text-sm text-gray-400">or click to select a .txt file</p>
                </>
              )}
            </div>

            {file && (
              <div className="mt-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Chat Name
                  </label>
                  <input
                    type="text"
                    value={chatName}
                    onChange={(e) => setChatName(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-green-400"
                    placeholder="e.g., Family Group, John Doe"
                  />
                </div>

                <button
                  onClick={handleUpload}
                  disabled={!chatName || isUploading}
                  className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Importing...' : 'Import Chat'}
                </button>
              </div>
            )}

            <button
              onClick={() => setShowInstructions(!showInstructions)}
              className="mt-4 text-sm text-green-400 hover:text-green-300 transition-colors flex items-center space-x-1 mx-auto"
            >
              <Smartphone className="w-4 h-4" />
              <span>How to export from WhatsApp?</span>
            </button>

            {showInstructions && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="mt-4 p-4 bg-gray-800/50 rounded-lg text-sm"
              >
                <div className="space-y-3">
                  <div>
                    <p className="font-medium text-green-400 mb-1">Android:</p>
                    <ol className="list-decimal list-inside text-gray-300 space-y-1">
                      <li>Open the chat in WhatsApp</li>
                      <li>Tap ⋮ → More → Export chat</li>
                      <li>Choose &quot;Without Media&quot;</li>
                      <li>Save and upload the .txt file</li>
                    </ol>
                  </div>
                  <div>
                    <p className="font-medium text-green-400 mb-1">iPhone:</p>
                    <ol className="list-decimal list-inside text-gray-300 space-y-1">
                      <li>Open the chat in WhatsApp</li>
                      <li>Tap contact name → Export Chat</li>
                      <li>Choose &quot;Without Media&quot;</li>
                      <li>Save and upload the .txt file</li>
                    </ol>
                  </div>
                </div>
              </motion.div>
            )}
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-8"
          >
            {result.success ? (
              <>
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Import Successful!</h3>
                <p className="text-gray-300 mb-4">{result.message}</p>
                {result.details && (
                  <div className="bg-gray-800/50 rounded-lg p-4 text-left">
                    <p className="text-sm text-gray-400">
                      Imported: <span className="text-white font-medium">{result.details.imported}</span> / {result.details.total}
                    </p>
                    {result.details.errors && result.details.errors.length > 0 && (
                      <div className="mt-2">
                        <p className="text-sm text-red-400">Some errors occurred:</p>
                        <ul className="text-xs text-gray-400 mt-1">
                          {result.details.errors.slice(0, 3).map((error, i) => (
                            <li key={i}>• {error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                <button
                  onClick={onClose}
                  className="mt-6 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  Done
                </button>
              </>
            ) : (
              <>
                <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Import Failed</h3>
                <p className="text-gray-300 mb-4">{result.message}</p>
                <button
                  onClick={() => {
                    setResult(null)
                    setFile(null)
                  }}
                  className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  Try Again
                </button>
              </>
            )}
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  )
} 