// import { useState, useEffect, useRef } from 'react';
// import axios from 'axios';
// import './App.css';

// const API_URL = 'http://localhost:8000';

// // Format error messages for better user experience
// const formatErrorMessage = (error) => {
//   const errorMsg = error.response?.data?.detail || error.message;

//   // Clean up ANSI color codes and error prefixes
//   const cleanedMsg = errorMsg
//     .replace(/```math0;31mERROR:```math0m/g, '')
//     .replace(/ERROR:/g, '')
//     .trim();

//   if (cleanedMsg.includes('403') || cleanedMsg.includes('Forbidden')) {
//     return `${cleanedMsg}\n\nTip: This video might be restricted. Try:\n- Using a different video\n- Checking if the video is private or age-restricted`;
//   }

//   if (cleanedMsg.includes('Connection reset') || cleanedMsg.includes('Connection aborted')) {
//     return `${cleanedMsg}\n\nTip: The website might be blocking automated access. Try:\n- Using a different website\n- Checking if the site is accessible in your browser`;
//   }

//   if (cleanedMsg.includes('LLM service is not available')) {
//     return `${cleanedMsg}\n\nTip: Make sure Ollama is running:\n- Run 'ollama serve' in a terminal\n- Check if Ollama is installed`;
//   }

//   return cleanedMsg;
// };

// function App() {
//   const [activeTab, setActiveTab] = useState('transcribe');
//   const [file, setFile] = useState(null);
//   const [url, setUrl] = useState('');
//   const [transcriptionResult, setTranscriptionResult] = useState(null);
//   const [chatMessage, setChatMessage] = useState('');
//   const [chatHistory, setChatHistory] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [inputType, setInputType] = useState('audio');
//   const [dragActive, setDragActive] = useState(false);
//   const [healthStatus, setHealthStatus] = useState(null);
  
//   // Attachment states
//   const [showAttachments, setShowAttachments] = useState(false);
//   const [attachments, setAttachments] = useState([]);
//   const [processingAttachments, setProcessingAttachments] = useState(false);
  
//   // Meeting summary states
//   const [showMeetingSummary, setShowMeetingSummary] = useState(false);
//   const [meetingSummaryResult, setMeetingSummaryResult] = useState(null);
//   const [meetingSummaryLoading, setMeetingSummaryLoading] = useState(false);
//   const [meetingContext, setMeetingContext] = useState('');
//   const [customInstructions, setCustomInstructions] = useState('');
//   const [selectedProvider, setSelectedProvider] = useState('gemini');
//   const [availableProviders, setAvailableProviders] = useState({});
  
//   const chatEndRef = useRef(null);

//   useEffect(() => {
//     checkBackendHealth();
//     const interval = setInterval(checkBackendHealth, 30000);
//     return () => clearInterval(interval);
//   }, []);

//   useEffect(() => {
//     scrollToBottom();
//   }, [chatHistory]);

//   // Add this useEffect to fetch available providers
//   useEffect(() => {
//     fetchAvailableProviders();
//   }, []);

//   const fetchAvailableProviders = async () => {
//     try {
//       const response = await axios.get(`${API_URL}/meeting/providers`);
//       setAvailableProviders(response.data.providers);
//       setSelectedProvider(response.data.current_provider);
//     } catch (error) {
//       console.error('Failed to fetch providers:', error);
//     }
//   };

//   const checkBackendHealth = async () => {
//     try {
//       const response = await axios.get(`${API_URL}/health`);
//       setHealthStatus(response.data);
//     } catch (error) {
//       console.error('Backend health check failed:', error);
//       setHealthStatus({
//         status: 'unknown',
//         whisper_model: 'unknown',
//         llm_available: false,
//         device: 'unknown'
//       });
//     }
//   };

//   const scrollToBottom = () => {
//     chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   const handleDrag = (e) => {
//     e.preventDefault();
//     e.stopPropagation();
//     if (e.type === 'dragenter' || e.type === 'dragover') {
//       setDragActive(true);
//     } else if (e.type === 'dragleave') {
//       setDragActive(false);
//     }
//   };

//   const handleDrop = (e) => {
//     e.preventDefault();
//     e.stopPropagation();
//     setDragActive(false);
//     if (e.dataTransfer.files && e.dataTransfer.files[0]) {
//       setFile(e.dataTransfer.files[0]);
//     }
//   };

//   const handleFileUpload = (e) => {
//     setFile(e.target.files[0]);
//   };

//   const handleTranscribe = async () => {
//     setLoading(true);
//     setTranscriptionResult(null);
//     setShowAttachments(false);
//     setAttachments([]);

//     try {
//       let response;

//       if (inputType === 'audio' || inputType === 'video') {
//         if (!file) {
//           alert('Please select a file');
//           setLoading(false);
//           return;
//         }

//         const formData = new FormData();
//         formData.append('file', file);

//         response = await axios.post(`${API_URL}/transcribe/${inputType}`, formData, {
//           headers: { 'Content-Type': 'multipart/form-data' },
//         });
//       } else if (inputType === 'youtube') {
//         if (!url) {
//           alert('Please enter a URL');
//           setLoading(false);
//           return;
//         }

//         response = await axios.post(`${API_URL}/transcribe/${inputType}`, { url });
//       }

//       setTranscriptionResult(response.data);
//       setShowAttachments(true); // Show attachment section after successful transcription
//     } catch (error) {
//       const errorMessage = formatErrorMessage(error);
//       alert('Error: ' + errorMessage);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleAddAttachment = () => {
//     setAttachments([...attachments, {
//       id: Date.now(),
//       type: 'audio',
//       file: null,
//       url: '',
//       result: null,
//       loading: false,
//       error: null
//     }]);
//   };

//   const handleRemoveAttachment = (id) => {
//     setAttachments(attachments.filter(att => att.id !== id));
//   };

//   const handleAttachmentTypeChange = (id, type) => {
//     setAttachments(attachments.map(att => 
//       att.id === id ? { ...att, type, file: null, url: '', error: null } : att
//     ));
//   };

//   const handleAttachmentFileChange = (id, file) => {
//     setAttachments(attachments.map(att => 
//       att.id === id ? { ...att, file, error: null } : att
//     ));
//   };

//   const handleAttachmentUrlChange = (id, url) => {
//     setAttachments(attachments.map(att => 
//       att.id === id ? { ...att, url, error: null } : att
//     ));
//   };

//   const processAttachments = async () => {
//     setProcessingAttachments(true);
    
//     const updatedAttachments = [...attachments];
    
//     for (let i = 0; i < updatedAttachments.length; i++) {
//       const attachment = updatedAttachments[i];
      
//       if (attachment.loading || attachment.result) continue;
      
//       updatedAttachments[i].loading = true;
//       setAttachments([...updatedAttachments]);
      
//       try {
//         let response;
        
//         if (attachment.type === 'audio' || attachment.type === 'video') {
//           if (!attachment.file) {
//             updatedAttachments[i].error = 'Please select a file';
//             updatedAttachments[i].loading = false;
//             continue;
//           }
          
//           const formData = new FormData();
//           formData.append('file', attachment.file);
          
//           response = await axios.post(
//             `${API_URL}/transcribe/${attachment.type}`,
//             formData,
//             { headers: { 'Content-Type': 'multipart/form-data' } }
//           );
//         } else if (attachment.type === 'youtube') {
//           if (!attachment.url) {
//             updatedAttachments[i].error = 'Please enter a YouTube URL';
//             updatedAttachments[i].loading = false;
//             continue;
//           }
          
//           response = await axios.post(
//             `${API_URL}/transcribe/youtube`,
//             { url: attachment.url }
//           );
//         } else if (attachment.type === 'url') {
//           if (!attachment.url) {
//             updatedAttachments[i].error = 'Please enter a URL';
//             updatedAttachments[i].loading = false;
//             continue;
//           }
          
//           response = await axios.post(
//             `${API_URL}/analyze/url`,
//             { url: attachment.url }
//           );
//         }
        
//         updatedAttachments[i].result = response.data;
//         updatedAttachments[i].loading = false;
//       } catch (error) {
//         updatedAttachments[i].error = formatErrorMessage(error);
//         updatedAttachments[i].loading = false;
//       }
      
//       setAttachments([...updatedAttachments]);
//     }
    
//     setProcessingAttachments(false);
//   };

//   const generateMeetingSummary = async () => {
//     setMeetingSummaryLoading(true);
    
//     try {
//       const summaryData = {
//         main_transcript: {
//           text: transcriptionResult.text,
//           formatted_text: transcriptionResult.formatted_text,
//           type: inputType
//         },
//         attachments: attachments
//           .filter(att => att.result)
//           .map(att => ({
//             type: att.type,
//             text: att.result.text || att.result.formatted_text,
//             url: att.url || null,
//             summary: att.result.summary || null
//           })),
//         context: meetingContext,
//         instructions: customInstructions,
//         provider: selectedProvider
//       };
      
//       const response = await axios.post(`${API_URL}/meeting/summarize`, summaryData);
//       setMeetingSummaryResult(response.data);
//       setShowMeetingSummary(true);
//     } catch (error) {
//       alert('Error generating meeting summary: ' + formatErrorMessage(error));
//     } finally {
//       setMeetingSummaryLoading(false);
//     }
//   };

//   const handleDownload = () => {
//     if (!transcriptionResult?.filename) return;
//     window.open(`${API_URL}/download/${transcriptionResult.filename}`, '_blank');
//   };

//   const handleChat = async () => {
//     if (!chatMessage.trim()) return;

//     setLoading(true);
//     const userMessage = { role: 'user', content: chatMessage };
//     setChatHistory((prev) => [...prev, userMessage]);
//     setChatMessage('');

//     try {
//       const response = await axios.post(`${API_URL}/chat`, { message: chatMessage });

//       const assistantMessage = {
//         role: 'assistant',
//         content: response.data.response,
//       };
//       setChatHistory((prev) => [...prev, assistantMessage]);
//     } catch (error) {
//       const errorMessage = formatErrorMessage(error);
//       alert('Error: ' + errorMessage);
//       setChatHistory((prev) => prev.slice(0, -1));
//     } finally {
//       setLoading(false);
//     }
//   };

//   const clearChat = () => {
//     setChatHistory([]);
//   };

//   const resetTranscription = () => {
//     setFile(null);
//     setUrl('');
//     setTranscriptionResult(null);
//     setShowAttachments(false);
//     setAttachments([]);
//     setShowMeetingSummary(false);
//     setMeetingSummaryResult(null);
//   };

//   return (
//     <div className="app">
//       <header className="app-header">
//         <h1>Multimodal Transcription & Local LLM</h1>
//         {healthStatus && (
//           <p>
//             Backend: {healthStatus.status} | Device: {healthStatus.device} | LLM:{' '}
//             {healthStatus.llm_available ? 'Ready' : 'Not Available'}
//           </p>
//         )}
//         <div className="tabs">
//           <button onClick={() => setActiveTab('transcribe')} className={activeTab === 'transcribe' ? 'active' : ''}>
//             Transcription
//           </button>
//           <button onClick={() => setActiveTab('chat')} className={activeTab === 'chat' ? 'active' : ''}>
//             Chat with LLM
//           </button>
//         </div>
//       </header>

//       <main>
//         {activeTab === 'transcribe' ? (
//           <div className="transcribe-section">
//             <div className="input-options">
//               {['audio', 'video', 'youtube'].map((type) => (
//                 <button
//                   key={type}
//                   className={inputType === type ? 'active' : ''}
//                   onClick={() => {
//                     setInputType(type);
//                     resetTranscription();
//                   }}
//                 >
//                   {type.toUpperCase()}
//                 </button>
//               ))}
//             </div>

//             {inputType === 'audio' || inputType === 'video' ? (
//               <div
//                 className={`file-upload ${dragActive ? 'drag-active' : ''}`}
//                 onDragEnter={handleDrag}
//                 onDragLeave={handleDrag}
//                 onDragOver={handleDrag}
//                 onDrop={handleDrop}
//               >
//                 <input
//                   type="file"
//                   accept={inputType === 'audio' ? 'audio/*' : 'video/*'}
//                   onChange={handleFileUpload}
//                 />
//                 {file ? <p>Selected: {file.name}</p> : <p>Drag or choose a file</p>}
//               </div>
//             ) : (
//               <input
//                 type="text"
//                 placeholder="Enter YouTube URL"
//                 value={url}
//                 onChange={(e) => setUrl(e.target.value)}
//               />
//             )}

//             <button onClick={handleTranscribe} disabled={loading || (!file && !url)}>
//               {loading ? 'Processing...' : 'Transcribe'}
//             </button>

//             {transcriptionResult && (
//               <div className="result">
//                 <h3>Transcription Result</h3>
//                 <pre>{transcriptionResult.formatted_text}</pre>
//                 <button onClick={handleDownload}>Download</button>
//                 <button onClick={resetTranscription}>Clear</button>
//               </div>
//             )}

//             {showAttachments && transcriptionResult && (
//               <div className="attachments-section">
//                 <h3>Additional Attachments (Optional)</h3>
//                 <p>Add more files to transcribe or URLs to analyze</p>
                
//                 {attachments.map((attachment) => (
//                   <div key={attachment.id} className="attachment-item">
//                     <div className="attachment-controls">
//                       <select 
//                         value={attachment.type} 
//                         onChange={(e) => handleAttachmentTypeChange(attachment.id, e.target.value)}
//                       >
//                         <option value="audio">Audio</option>
//                                                 <option value="video">Video</option>
//                         <option value="youtube">YouTube</option>
//                         <option value="url">URL (Summary)</option>
//                       </select>
                      
//                       {(attachment.type === 'audio' || attachment.type === 'video') ? (
//                         <input
//                           type="file"
//                           accept={attachment.type === 'audio' ? 'audio/*' : 'video/*'}
//                           onChange={(e) => handleAttachmentFileChange(attachment.id, e.target.files[0])}
//                         />
//                       ) : (
//                         <input
//                           type="text"
//                           placeholder={attachment.type === 'youtube' ? 'YouTube URL' : 'Any URL'}
//                           value={attachment.url}
//                           onChange={(e) => handleAttachmentUrlChange(attachment.id, e.target.value)}
//                         />
//                       )}
                      
//                       <button onClick={() => handleRemoveAttachment(attachment.id)}>Remove</button>
//                     </div>
                    
//                     {attachment.loading && <p className="loading-text">Processing...</p>}
//                     {attachment.error && <p className="error-text">Error: {attachment.error}</p>}
//                     {attachment.result && (
//                       <div className="attachment-result">
//                         <pre>{attachment.result.formatted_text || attachment.result.summary}</pre>
//                       </div>
//                     )}
//                   </div>
//                 ))}
                
//                 <button onClick={handleAddAttachment} className="add-attachment-btn">
//                   Add Attachment
//                 </button>
                
//                 {attachments.length > 0 && (
//                   <button 
//                     onClick={processAttachments} 
//                     disabled={processingAttachments}
//                     className="process-attachments-btn"
//                   >
//                     {processingAttachments ? 'Processing...' : 'Process All Attachments'}
//                   </button>
//                 )}
//               </div>
//             )}

//             {transcriptionResult && (
//               <div className="meeting-summary-section">
//                 <h3>Professional Meeting Summary</h3>
//                 <p>Generate a structured meeting summary with key points and action items</p>
                
//                 <div className="provider-selection">
//                   <label>Select LLM Provider:</label>
//                   <div className="provider-options">
//                     <label className="provider-option">
//                       <input
//                         type="radio"
//                         name="provider"
//                         value="gemini"
//                         checked={selectedProvider === 'gemini'}
//                         onChange={(e) => setSelectedProvider(e.target.value)}
//                         disabled={!availableProviders.gemini}
//                       />
//                       <span>Google Gemini {!availableProviders.gemini && '(Not configured)'}</span>
//                     </label>
//                     <label className="provider-option">
//                       <input
//                         type="radio"
//                         name="provider"
//                         value="openai"
//                         checked={selectedProvider === 'openai'}
//                         onChange={(e) => setSelectedProvider(e.target.value)}
//                         disabled={!availableProviders.openai}
//                       />
//                       <span>OpenAI GPT {!availableProviders.openai && '(Not configured)'}</span>
//                     </label>
//                     <label className="provider-option">
//                       <input
//                         type="radio"
//                         name="provider"
//                         value="claude"
//                         checked={selectedProvider === 'claude'}
//                         onChange={(e) => setSelectedProvider(e.target.value)}
//                         disabled={!availableProviders.claude}
//                       />
//                       <span>Anthropic Claude {!availableProviders.claude && '(Not configured)'}</span>
//                     </label>
//                   </div>
//                 </div>
                
//                 <div className="meeting-inputs">
//                   <input
//                     type="text"
//                     placeholder="Meeting context (e.g., 'Q4 Planning Meeting with Product Team')"
//                     value={meetingContext}
//                     onChange={(e) => setMeetingContext(e.target.value)}
//                     className="meeting-context-input"
//                   />
                  
//                   <textarea
//                     placeholder="Custom instructions (e.g., 'Focus on budget discussions and timeline changes')"
//                     value={customInstructions}
//                     onChange={(e) => setCustomInstructions(e.target.value)}
//                     className="custom-instructions-input"
//                   />
//                 </div>
                
//                 <button 
//                   onClick={generateMeetingSummary}
//                   disabled={meetingSummaryLoading || !availableProviders[selectedProvider]}
//                   className="generate-meeting-summary-btn"
//                 >
//                   {meetingSummaryLoading ? 'Generating Professional Summary...' : 'Generate Meeting Summary'}
//                 </button>
                
//                 {showMeetingSummary && meetingSummaryResult && (
//                   <div className="meeting-summary-result">
//                     <div className="summary-section">
//                       <h4>Executive Summary</h4>
//                       <div className="summary-content">
//                         <pre>{meetingSummaryResult.summary}</pre>
//                       </div>
//                     </div>
                    
//                     <div className="insights-section">
//                       <h4>Strategic Insights</h4>
//                       <div className="insights-content">
//                         <pre>{meetingSummaryResult.insights}</pre>
//                       </div>
//                     </div>
                    
//                     <div className="actions-section">
//                       <h4>Action Items</h4>
//                       <div className="actions-content">
//                         <pre>{meetingSummaryResult.action_items}</pre>
//                       </div>
//                     </div>
                    
//                     <div className="statistics">
//                       <p>Transcript cleaned by {meetingSummaryResult.statistics.reduction_percentage}%</p>
//                       <p>Provider: {meetingSummaryResult.provider.toUpperCase()}</p>
//                     </div>
                    
//                     <button 
//                       onClick={() => window.open(`${API_URL}/download/${meetingSummaryResult.filename}`, '_blank')}
//                       className="download-btn"
//                     >
//                       Download Complete Summary
//                     </button>
//                   </div>
//                 )}
//               </div>
//             )}
//           </div>
//         ) : (
//           <div className="chat-section">
//             <div className="chat-history">
//               {chatHistory.map((msg, index) => (
//                 <div key={index} className={`message ${msg.role}`}>
//                   <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
//                 </div>
//               ))}
//               {loading && <div className="message assistant">Typing...</div>}
//               <div ref={chatEndRef} />
//             </div>
//             <div className="chat-input">
//               <input
//                 type="text"
//                 placeholder="Type your message..."
//                 value={chatMessage}
//                 onChange={(e) => setChatMessage(e.target.value)}
//                 onKeyDown={(e) => e.key === 'Enter' && handleChat()}
//                 disabled={loading}
//               />
//               <button onClick={handleChat} disabled={loading || !chatMessage.trim()}>
//                 Send
//               </button>
//               <button onClick={clearChat}>Clear</button>
//             </div>
//           </div>
//         )}
//       </main>

//       <footer>
//         <p>Powered by Whisper AI and Ollama</p>
//       </footer>
//     </div>
//   );
// }

// export default App;
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

// Format error messages for better user experience
const formatErrorMessage = (error) => {
  const errorMsg = error.response?.data?.detail || error.message;

  // Clean up ANSI color codes and error prefixes
  const cleanedMsg = errorMsg
    .replace(/```math0;31mERROR:```math0m/g, '')
    .replace(/ERROR:/g, '')
    .trim();

  if (cleanedMsg.includes('403') || cleanedMsg.includes('Forbidden')) {
    return `${cleanedMsg}\n\nTip: This video might be restricted. Try:\n- Using a different video\n- Checking if the video is private or age-restricted`;
  }

  if (cleanedMsg.includes('Connection reset') || cleanedMsg.includes('Connection aborted')) {
    return `${cleanedMsg}\n\nTip: The website might be blocking automated access. Try:\n- Using a different website\n- Checking if the site is accessible in your browser`;
  }

  if (cleanedMsg.includes('LLM service is not available')) {
    return `${cleanedMsg}\n\nTip: Make sure Ollama is running:\n- Run 'ollama serve' in a terminal\n- Check if Ollama is installed`;
  }

  return cleanedMsg;
};

function App() {
  const [activeTab, setActiveTab] = useState('transcribe');
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [transcriptionResult, setTranscriptionResult] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputType, setInputType] = useState('audio');
  const [dragActive, setDragActive] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);
  
  // Attachment states
  const [showAttachments, setShowAttachments] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [processingAttachments, setProcessingAttachments] = useState(false);
  
  // Meeting summary states
  const [showMeetingSummary, setShowMeetingSummary] = useState(false);
  const [meetingSummaryResult, setMeetingSummaryResult] = useState(null);
  const [meetingSummaryLoading, setMeetingSummaryLoading] = useState(false);
  const [meetingContext, setMeetingContext] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [availableProviders, setAvailableProviders] = useState({});
  
  // Context-aware chat states
  const [chatProvider, setChatProvider] = useState('gemini');
  const [chatContext, setChatContext] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [useContext, setUseContext] = useState(true);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  useEffect(() => {
    fetchAvailableProviders();
  }, []);

  const fetchAvailableProviders = async () => {
    try {
      const response = await axios.get(`${API_URL}/meeting/providers`);
      setAvailableProviders(response.data.providers);
      setSelectedProvider(response.data.current_provider);
      setChatProvider(response.data.current_provider);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    }
  };

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealthStatus(response.data);
    } catch (error) {
      console.error('Backend health check failed:', error);
      setHealthStatus({
        status: 'unknown',
        whisper_model: 'unknown',
        llm_available: false,
        device: 'unknown'
      });
    }
  };

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTranscribe = async () => {
    setLoading(true);
    setTranscriptionResult(null);
    setShowAttachments(false);
    setAttachments([]);

    try {
      let response;

      if (inputType === 'audio' || inputType === 'video') {
        if (!file) {
          alert('Please select a file');
          setLoading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', file);

        response = await axios.post(`${API_URL}/transcribe/${inputType}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else if (inputType === 'youtube') {
        if (!url) {
          alert('Please enter a URL');
          setLoading(false);
          return;
        }

        response = await axios.post(`${API_URL}/transcribe/${inputType}`, { url });
      }

      setTranscriptionResult(response.data);
      setShowAttachments(true);
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      alert('Error: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAttachment = () => {
    setAttachments([...attachments, {
      id: Date.now(),
      type: 'audio',
      file: null,
      url: '',
      result: null,
      loading: false,
      error: null
    }]);
  };

  const handleRemoveAttachment = (id) => {
        setAttachments(attachments.filter(att => att.id !== id));
  };

  const handleAttachmentTypeChange = (id, type) => {
    setAttachments(attachments.map(att => 
      att.id === id ? { ...att, type, file: null, url: '', error: null } : att
    ));
  };

  const handleAttachmentFileChange = (id, file) => {
    setAttachments(attachments.map(att => 
      att.id === id ? { ...att, file, error: null } : att
    ));
  };

  const handleAttachmentUrlChange = (id, url) => {
    setAttachments(attachments.map(att => 
      att.id === id ? { ...att, url, error: null } : att
    ));
  };

  const processAttachments = async () => {
    setProcessingAttachments(true);
    
    const updatedAttachments = [...attachments];
    
    for (let i = 0; i < updatedAttachments.length; i++) {
      const attachment = updatedAttachments[i];
      
      if (attachment.loading || attachment.result) continue;
      
      updatedAttachments[i].loading = true;
      setAttachments([...updatedAttachments]);
      
      try {
        let response;
        
        if (attachment.type === 'audio' || attachment.type === 'video') {
          if (!attachment.file) {
            updatedAttachments[i].error = 'Please select a file';
            updatedAttachments[i].loading = false;
            continue;
          }
          
          const formData = new FormData();
          formData.append('file', attachment.file);
          
          response = await axios.post(
            `${API_URL}/transcribe/${attachment.type}`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
          );
        } else if (attachment.type === 'youtube') {
          if (!attachment.url) {
            updatedAttachments[i].error = 'Please enter a YouTube URL';
            updatedAttachments[i].loading = false;
            continue;
          }
          
          response = await axios.post(
            `${API_URL}/transcribe/youtube`,
            { url: attachment.url }
          );
        } else if (attachment.type === 'url') {
          if (!attachment.url) {
            updatedAttachments[i].error = 'Please enter a URL';
            updatedAttachments[i].loading = false;
            continue;
          }
          
          response = await axios.post(
            `${API_URL}/analyze/url`,
            { url: attachment.url }
          );
        }
        
        updatedAttachments[i].result = response.data;
        updatedAttachments[i].loading = false;
      } catch (error) {
        updatedAttachments[i].error = formatErrorMessage(error);
        updatedAttachments[i].loading = false;
      }
      
      setAttachments([...updatedAttachments]);
    }
    
    setProcessingAttachments(false);
  };

  const generateMeetingSummary = async () => {
    setMeetingSummaryLoading(true);
    
    try {
      const summaryData = {
        main_transcript: {
          text: transcriptionResult.text,
          formatted_text: transcriptionResult.formatted_text,
          type: inputType
        },
        attachments: attachments
          .filter(att => att.result)
          .map(att => ({
            type: att.type,
            text: att.result.text || att.result.formatted_text,
            url: att.url || null,
            summary: att.result.summary || null
          })),
        context: meetingContext,
        instructions: customInstructions,
        provider: selectedProvider
      };
      
      const response = await axios.post(`${API_URL}/meeting/summarize`, summaryData);
      setMeetingSummaryResult(response.data);
      setShowMeetingSummary(true);
    } catch (error) {
      alert('Error generating meeting summary: ' + formatErrorMessage(error));
    } finally {
      setMeetingSummaryLoading(false);
    }
  };

  const handleDownload = () => {
    if (!transcriptionResult?.filename) return;
    window.open(`${API_URL}/download/${transcriptionResult.filename}`, '_blank');
  };

  // Prepare context from transcription and summary
  const prepareChatContext = () => {
    const context = {};
    
    if (transcriptionResult) {
      context.transcription = transcriptionResult.text || transcriptionResult.formatted_text;
    }
    
    if (meetingSummaryResult) {
      context.summary = meetingSummaryResult.summary;
      context.insights = meetingSummaryResult.insights;
      context.action_items = meetingSummaryResult.action_items;
    }
    
    // Add attachment summaries
    if (attachments.length > 0) {
      context.attachments = attachments
        .filter(att => att.result)
        .map(att => ({
          type: att.type,
          content: att.result.text || att.result.summary || att.result.formatted_text
        }));
    }
    
    return context;
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) return;

    setLoading(true);
    const userMessage = { role: 'user', content: chatMessage };
    setChatHistory((prev) => [...prev, userMessage]);
    setChatMessage('');

    try {
      let response;
      
      // Use context-aware chat if we have transcription or summary
      if (useContext && (transcriptionResult || meetingSummaryResult)) {
        const context = prepareChatContext();
        
        response = await axios.post(`${API_URL}/chat/context`, {
          message: chatMessage,
          session_id: sessionId,
          context: chatContext || context,
          provider: chatProvider
        });
        
        // Store context for future messages
        if (!chatContext) {
          setChatContext(context);
        }
      } else {
        // Fall back to regular chat
        response = await axios.post(`${API_URL}/chat`, { message: chatMessage });
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        provider: response.data.provider
      };
      setChatHistory((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = formatErrorMessage(error);
      alert('Error: ' + errorMessage);
      setChatHistory((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
  };

  const clearChatContext = async () => {
    try {
      await axios.post(`${API_URL}/chat/clear-context`, { session_id: sessionId });
      setChatContext(null);
      alert('Chat context cleared');
    } catch (error) {
      console.error('Failed to clear context:', error);
    }
  };

  const resetTranscription = () => {
    setFile(null);
    setUrl('');
    setTranscriptionResult(null);
    setShowAttachments(false);
    setAttachments([]);
    setShowMeetingSummary(false);
    setMeetingSummaryResult(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Multimodal Transcription & Local LLM</h1>
        {healthStatus && (
          <p>
            Backend: {healthStatus.status} | Device: {healthStatus.device} | LLM:{' '}
            {healthStatus.llm_available ? 'Ready' : 'Not Available'}
          </p>
        )}
        <div className="tabs">
          <button onClick={() => setActiveTab('transcribe')} className={activeTab === 'transcribe' ? 'active' : ''}>
            Transcription
          </button>
          <button onClick={() => setActiveTab('chat')} className={activeTab === 'chat' ? 'active' : ''}>
            Chat with LLM
          </button>
        </div>
      </header>

      <main>
        {activeTab === 'transcribe' ? (
          <div className="transcribe-section">
            <div className="input-options">
              {['audio', 'video', 'youtube'].map((type) => (
                <button
                  key={type}
                  className={inputType === type ? 'active' : ''}
                  onClick={() => {
                    setInputType(type);
                    resetTranscription();
                  }}
                >
                  {type.toUpperCase()}
                </button>
              ))}
            </div>

            {inputType === 'audio' || inputType === 'video' ? (
              <div
                className={`file-upload ${dragActive ? 'drag-active' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept={inputType === 'audio' ? 'audio/*' : 'video/*'}
                  onChange={handleFileUpload}
                />
                {file ? <p>Selected: {file.name}</p> : <p>Drag or choose a file</p>}
              </div>
            ) : (
              <input
                type="text"
                placeholder="Enter YouTube URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            )}

            <button onClick={handleTranscribe} disabled={loading || (!file && !url)}>
              {loading ? 'Processing...' : 'Transcribe'}
            </button>

            {transcriptionResult && (
              <div className="result">
                <h3>Transcription Result</h3>
                <pre>{transcriptionResult.formatted_text}</pre>
                <button onClick={handleDownload}>Download</button>
                <button onClick={resetTranscription}>Clear</button>
              </div>
            )}

            {showAttachments && transcriptionResult && (
              <div className="attachments-section">
                <h3>Additional Attachments (Optional)</h3>
                <p>Add more files to transcribe or URLs to analyze</p>
                
                {attachments.map((attachment) => (
                  <div key={attachment.id} className="attachment-item">
                    <div className="attachment-controls">
                      <select 
                        value={attachment.type} 
                        onChange={(e) => handleAttachmentTypeChange(attachment.id, e.target.value)}
                      >
                        <option value="audio">Audio</option>
                        <option value="video">Video</option>
                        <option value="youtube">YouTube</option>
                        <option value="url">URL (Summary)</option>
                      </select>
                      
                      {(attachment.type === 'audio' || attachment.type === 'video') ? (
                        <input
                          type="file"
                          accept={attachment.type === 'audio' ? 'audio/*' : 'video/*'}
                          onChange={(e) => handleAttachmentFileChange(attachment.id, e.target.files[0])}
                        />
                      ) : (
                        <input
                          type="text"
                          placeholder={attachment.type === 'youtube' ? 'YouTube URL' : 'Any URL'}
                          value={attachment.url}
                          onChange={(e) => handleAttachmentUrlChange(attachment.id, e.target.value)}
                        />
                      )}
                      
                      <button onClick={() => handleRemoveAttachment(attachment.id)}>Remove</button>
                    </div>
                    
                    {attachment.loading && <p className="loading-text">Processing...</p>}
                    {attachment.error && <p className="error-text">Error: {attachment.error}</p>}
                    {attachment.result && (
                      <div className="attachment-result">
                        <pre>{attachment.result.formatted_text || attachment.result.summary}</pre>
                      </div>
                    )}
                  </div>
                ))}
                
                <button onClick={handleAddAttachment} className="add-attachment-btn">
                  Add Attachment
                </button>
                
                {attachments.length > 0 && (
                  <button 
                    onClick={processAttachments} 
                    disabled={processingAttachments}
                    className="process-attachments-btn"
                  >
                    {processingAttachments ? 'Processing...' : 'Process All Attachments'}
                  </button>
                )}
              </div>
            )}

            {transcriptionResult && (
              <div className="meeting-summary-section">
                <h3>Professional Meeting Summary</h3>
                <p>Generate a structured meeting summary with key points and action items</p>
                
                <div className="provider-selection">
                  <label>Select LLM Provider:</label>
                  <div className="provider-options">
                    <label className="provider-option">
                      <input
                        type="radio"
                        name="provider"
                        value="gemini"
                        checked={selectedProvider === 'gemini'}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        disabled={!availableProviders.gemini}
                      />
                      <span>Google Gemini {!availableProviders.gemini && '(Not configured)'}</span>
                    </label>
                    <label className="provider-option">
                      <input
                        type="radio"
                        name="provider"
                        value="openai"
                        checked={selectedProvider === 'openai'}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        disabled={!availableProviders.openai}
                      />
                      <span>OpenAI GPT {!availableProviders.openai && '(Not configured)'}</span>
                    </label>
                    <label className="provider-option">
                      <input
                        type="radio"
                        name="provider"
                        value="claude"
                        checked={selectedProvider === 'claude'}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        disabled={!availableProviders.claude}
                      />
                      <span>Anthropic Claude {!availableProviders.claude && '(Not configured)'}</span>
                    </label>
                  </div>
                </div>
                
                <div className="meeting-inputs">
                  <input
                    type="text"
                    placeholder="Meeting context (e.g., 'Q4 Planning Meeting with Product Team')"
                    value={meetingContext}
                    onChange={(e) => setMeetingContext(e.target.value)}
                    className="meeting-context-input"
                  />
                  
                  <textarea
                    placeholder="Custom instructions (e.g., 'Focus on budget discussions and timeline changes')"
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    className="custom-instructions-input"
                  />
                </div>
                
                <button 
                  onClick={generateMeetingSummary}
                  disabled={meetingSummaryLoading || !availableProviders[selectedProvider]}
                  className="generate-meeting-summary-btn"
                >
                  {meetingSummaryLoading ? 'Generating Professional Summary...' : 'Generate Meeting Summary'}
                </button>
                
                {showMeetingSummary && meetingSummaryResult && (
                  <div className="meeting-summary-result">
                    <div className="summary-section">
                      <h4>Executive Summary</h4>
                      <div className="summary-content">
                        <pre>{meetingSummaryResult.summary}</pre>
                                            </div>
                    </div>
                    
                    <div className="insights-section">
                      <h4>Strategic Insights</h4>
                      <div className="insights-content">
                        <pre>{meetingSummaryResult.insights}</pre>
                      </div>
                    </div>
                    
                    <div className="actions-section">
                      <h4>Action Items</h4>
                      <div className="actions-content">
                        <pre>{meetingSummaryResult.action_items}</pre>
                      </div>
                    </div>
                    
                    <div className="statistics">
                      <p>Transcript cleaned by {meetingSummaryResult.statistics.reduction_percentage}%</p>
                      <p>Provider: {meetingSummaryResult.provider.toUpperCase()}</p>
                    </div>
                    
                    <button 
                      onClick={() => window.open(`${API_URL}/download/${meetingSummaryResult.filename}`, '_blank')}
                      className="download-btn"
                    >
                      Download Complete Summary
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="chat-section">
            <div className="chat-header">
              <h3>AI Assistant Chat</h3>
              {(transcriptionResult || meetingSummaryResult) && (
                <div className="chat-options">
                  <label className="context-toggle">
                    <input
                      type="checkbox"
                      checked={useContext}
                      onChange={(e) => setUseContext(e.target.checked)}
                    />
                    Use meeting context
                  </label>
                  
                  <select 
                    value={chatProvider} 
                    onChange={(e) => setChatProvider(e.target.value)}
                    className="provider-select"
                  >
                    <option value="gemini" disabled={!availableProviders.gemini}>
                      Gemini {!availableProviders.gemini && '(Not configured)'}
                    </option>
                    <option value="openai" disabled={!availableProviders.openai}>
                      OpenAI {!availableProviders.openai && '(Not configured)'}
                    </option>
                    <option value="claude" disabled={!availableProviders.claude}>
                      Claude {!availableProviders.claude && '(Not configured)'}
                    </option>
                    <option value="ollama" disabled={!healthStatus?.llm_available}>
                      Ollama (Local) {!healthStatus?.llm_available && '(Not available)'}
                    </option>
                  </select>
                </div>
              )}
            </div>
            
            {useContext && (transcriptionResult || meetingSummaryResult) && (
              <div className="context-info">
                <p>🎯 Context-aware mode: The AI has access to your meeting transcription and summary</p>
                <p>Try asking questions like:</p>
                <ul>
                  <li>"What were the main decisions made in the meeting?"</li>
                  <li>"Who is responsible for the budget review?"</li>
                  <li>"What are the risks mentioned in the discussion?"</li>
                  <li>"Can you predict potential challenges based on this meeting?"</li>
                  <li>"Create a follow-up email based on the action items"</li>
                  <li>"What timeline was discussed for the project?"</li>
                  <li>"Summarize the budget concerns raised"</li>
                  <li>"Generate a status report based on this meeting"</li>
                </ul>
              </div>
            )}
            
            <div className="chat-history">
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <strong>{msg.role === 'user' ? 'You' : `AI (${msg.provider || 'Local'})`}:</strong> 
                  <div className="message-content">{msg.content}</div>
                </div>
              ))}
              {loading && <div className="message assistant">Thinking...</div>}
              <div ref={chatEndRef} />
            </div>
            
            <div className="chat-input">
              <input
                type="text"
                placeholder={useContext && (transcriptionResult || meetingSummaryResult) 
                  ? "Ask about the meeting..." 
                  : "Type your message..."}
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                disabled={loading}
              />
              <button onClick={handleChat} disabled={loading || !chatMessage.trim()}>
                Send
              </button>
              <button onClick={clearChat}>Clear Chat</button>
              {chatContext && (
                <button onClick={clearChatContext}>Clear Context</button>
              )}
            </div>
          </div>
        )}
      </main>

      <footer>
        <p>Powered by Whisper AI and Multiple LLM Providers</p>
      </footer>
    </div>
  );
}

export default App;