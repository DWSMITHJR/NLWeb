import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box, Typography, TextField, Button, Paper, CircularProgress, AppBar, Toolbar } from '@mui/material';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [docContent, setDocContent] = useState('');
  const [docId, setDocId] = useState('');

  const handleQuery = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const result = await axios.post(`/query`, {
        query: query,
        context: {}
      });
      setResponse(result.data);
    } catch (error) {
      console.error('Error querying API:', error);
      setResponse({
        answer: 'Error processing your query. Please try again.',
        sources: [],
        confidence: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddDocument = async () => {
    if (!docContent.trim() || !docId.trim()) return;
    
    try {
      await axios.post(`/documents`, {
        id: docId,
        content: docContent,
        metadata: {}
      });
      alert('Document added successfully!');
      setDocContent('');
      setDocId('');
    } catch (error) {
      console.error('Error adding document:', error);
      alert('Failed to add document');
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NLWeb AutoRAG
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>Add Knowledge</Typography>
          <TextField
            fullWidth
            label="Document ID"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
            margin="normal"
            variant="outlined"
          />
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Document Content"
            value={docContent}
            onChange={(e) => setDocContent(e.target.value)}
            margin="normal"
            variant="outlined"
          />
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleAddDocument}
              disabled={!docContent.trim() || !docId.trim()}
            >
              Add Document
            </Button>
          </Box>
        </Paper>

        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Ask a Question</Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask me anything..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              disabled={loading}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleQuery}
              disabled={!query.trim() || loading}
              sx={{ minWidth: 120 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Ask'}
            </Button>
          </Box>

          {response && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>Response</Typography>
              <Box sx={{ 
                p: 2, 
                bgcolor: 'background.default', 
                borderRadius: 1,
                '& pre': { 
                  bgcolor: 'rgba(0,0,0,0.1)', 
                  p: 2, 
                  borderRadius: 1,
                  overflowX: 'auto'
                },
                '& code': {
                  fontFamily: 'monospace',
                  fontSize: '0.9em'
                }
              }}>
                <ReactMarkdown 
                  rehypePlugins={[rehypeRaw]} 
                  remarkPlugins={[remarkGfm]}
                >
                  {response.answer}
                </ReactMarkdown>
              </Box>
              
              {response.sources && response.sources.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary">Sources:</Typography>
                  <ul>
                    {response.sources.map((source, index) => (
                      <li key={index}>
                        <Typography variant="body2">{source}</Typography>
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
              
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                Confidence: {(response.confidence * 100).toFixed(1)}%
              </Typography>
            </Box>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;
