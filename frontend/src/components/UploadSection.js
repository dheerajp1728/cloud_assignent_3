import React, { useState } from 'react';
import axios from 'axios';

const API_GATEWAY_URL = 'https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod';
const API_KEY = 'EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4';

function UploadSection({ showMessage }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [customLabels, setCustomLabels] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
      } else {
        showMessage('Please select an image file', 'error');
        e.target.value = '';
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      showMessage('Please select a file to upload', 'error');
      return;
    }

    setUploading(true);

    try {
      const labels = customLabels
        .split(',')
        .map(label => label.trim())
        .filter(label => label);

      const headers = {
        'x-api-key': API_KEY,
        'Content-Type': selectedFile.type || 'image/jpeg'
      };

      if (labels.length > 0) {
        headers['x-amz-meta-customLabels'] = labels.join(',');
      }

      // Read file as ArrayBuffer to preserve binary data
      const fileBuffer = await selectedFile.arrayBuffer();

      const response = await axios.put(
        `${API_GATEWAY_URL}/upload/${encodeURIComponent(selectedFile.name)}`,
        fileBuffer,
        { 
          headers,
          maxContentLength: Infinity,
          maxBodyLength: Infinity
        }
      );

      if (response.status === 200) {
        showMessage('Photo uploaded successfully!', 'success');
        setSelectedFile(null);
        setCustomLabels('');
        document.querySelector('input[type="file"]').value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
      showMessage(`Upload failed: ${error.response?.data?.message || error.message}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="section">
      <h2>📤 Upload Photo</h2>
      <form onSubmit={handleUpload}>
        <div className="upload-container">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <button type="submit" disabled={uploading || !selectedFile}>
            {uploading && <span className="spinner"></span>}
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>

        <div className="custom-labels">
          <label htmlFor="customLabels">
            Custom Labels (optional)
          </label>
          <input
            type="text"
            id="customLabels"
            placeholder="e.g., vacation, birthday, family"
            value={customLabels}
            onChange={(e) => setCustomLabels(e.target.value)}
            disabled={uploading}
          />
          <small>Separate multiple labels with commas</small>
        </div>
      </form>
    </div>
  );
}

export default UploadSection;
