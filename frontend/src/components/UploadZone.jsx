import React, { useCallback, useState } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function UploadZone({ onUploadComplete }) {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
            setError(null);
        }
    }, []);

    const handleFileSelect = useCallback((e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
        }
    }, []);

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Use relative path assuming proxy or CORS setup
            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            onUploadComplete(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={twMerge(
                    "border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 ease-in-out cursor-pointer",
                    isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400 bg-white",
                    file && "border-green-500 bg-green-50"
                )}
            >
                <input
                    type="file"
                    className="hidden"
                    id="file-upload"
                    onChange={handleFileSelect}
                    accept=".pdf,.txt,audio/*,video/*"
                />

                {!file ? (
                    <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-4">
                        <div className="p-4 bg-blue-100 rounded-full text-blue-600">
                            <Upload size={32} />
                        </div>
                        <div>
                            <p className="text-lg font-semibold text-gray-700">Click to upload or drag and drop</p>
                            <p className="text-sm text-gray-500 mt-1">PDF, Audio, Video, or Text</p>
                        </div>
                    </label>
                ) : (
                    <div className="flex flex-col items-center gap-4">
                        <div className="p-4 bg-green-100 rounded-full text-green-600">
                            <File size={32} />
                        </div>
                        <div>
                            <p className="text-lg font-semibold text-gray-700">{file.name}</p>
                            <p className="text-sm text-gray-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                        <div className="flex gap-3 mt-2">
                            <button
                                onClick={() => setFile(null)}
                                className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                            >
                                Change File
                            </button>
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                {uploading ? 'Uploading...' : 'Start Processing'}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}
