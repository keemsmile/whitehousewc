import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Button,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Download as DownloadIcon 
} from '@mui/icons-material';
import ReactWordcloud from 'react-wordcloud';
import axios from 'axios';

const wordcloudOptions = {
  colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
  enableTooltip: true,
  deterministic: false,
  fontFamily: 'impact',
  fontSizes: [20, 60],
  fontStyle: 'normal',
  fontWeight: 'normal',
  padding: 1,
  rotations: 3,
  rotationAngles: [0, 90],
  scale: 'sqrt',
  spiral: 'archimedean',
  transitionDuration: 1000
};

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/articles');
      setArticles(response.data);
    } catch (error) {
      console.error('Error fetching articles:', error);
    }
    setLoading(false);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post('http://localhost:5000/api/refresh');
      await fetchArticles();
    } catch (error) {
      console.error('Error refreshing articles:', error);
    }
    setRefreshing(false);
  };

  const handleDownload = async (articleId) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/articles/${articleId}/download`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', response.headers['content-disposition']?.split('filename=')[1] || 'transcript.txt');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading transcript:', error);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            White House Briefing Room
          </Typography>
          <IconButton
            color="inherit"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {articles.map((article) => (
              <Card key={article.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h5" component="div" gutterBottom>
                    {article.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Published: {new Date(article.created_at).toLocaleDateString()}
                  </Typography>
                  
                  {/* Word Cloud */}
                  <Box sx={{ height: 300, width: '100%', mb: 2 }}>
                    {article.word_frequencies.length > 0 ? (
                      <ReactWordcloud 
                        words={article.word_frequencies} 
                        options={wordcloudOptions}
                      />
                    ) : (
                      <Typography variant="body2" color="text.secondary" align="center">
                        No word cloud data available
                      </Typography>
                    )}
                  </Box>

                  <Button 
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload(article.id)}
                    color="primary"
                  >
                    Download Transcript
                  </Button>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Container>
    </Box>
  );
}

export default App;
