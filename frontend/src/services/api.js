import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const uploadAudio = async (audioBlob, filename, mode = 'note') => {
    const formData = new FormData();
    formData.append('file', audioBlob, filename);
    formData.append('mode', mode);

    try {
        const response = await axios.post(`${API_URL}/record`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error("Upload failed", error);
        throw error;
    }
};
